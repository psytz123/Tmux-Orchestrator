"""
Model Training Pipeline for Demand Forecasting
Coordinates training of Prophet, XGBoost, and LightGBM models
"""
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from .forecasting_models import (
    ProphetForecastModel,
    XGBoostForecastModel, 
    LightGBMForecastModel,
    create_demand_time_series
)
from ..ml.model_evaluator import ModelEvaluator
from ...data.erp_loader import ERPDataLoader

logger = logging.getLogger(__name__)


class ForecastModelTrainer:
    """Comprehensive training pipeline for all forecasting models"""
    
    def __init__(self, models_dir: str = "models", data_dir: str = None):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.data_dir = data_dir
        self.erp_loader = ERPDataLoader(data_dir) if data_dir else None
        
        # Initialize models
        self.prophet_model = ProphetForecastModel()
        self.xgboost_model = XGBoostForecastModel()
        self.lightgbm_model = LightGBMForecastModel()
        
        # Model evaluator
        self.evaluator = ModelEvaluator()
        
        # Training results
        self.training_results = {}
        self.model_performance = {}
        
    def load_training_data(self, use_real_data: bool = True) -> pd.DataFrame:
        """Load and prepare training data"""
        
        if use_real_data and self.erp_loader:
            try:
                logger.info("Loading real ERP data for training...")
                
                # Load ERP data
                erp_data = self.erp_loader.load_all_data()
                
                # Convert to time series
                time_series = create_demand_time_series(erp_data)
                
                if not time_series.empty:
                    logger.info(f"Successfully loaded {len(time_series)} days of real demand data")
                    return time_series
                else:
                    logger.warning("Real data empty, falling back to synthetic data")
                    
            except Exception as e:
                logger.error(f"Error loading real data: {e}")
                logger.info("Falling back to synthetic data")
        
        # Generate synthetic training data with realistic textile patterns
        logger.info("Generating synthetic training data...")
        return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self, days: int = 180) -> pd.DataFrame:
        """Generate realistic synthetic demand data for textile industry"""
        
        np.random.seed(42)  # For reproducibility
        
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            periods=days,
            freq='D'
        )
        
        # Base demand with multiple patterns
        base_demand = 120
        
        # Weekly seasonality (lower on weekends)
        weekly_pattern = 20 * np.sin(2 * np.pi * np.arange(days) / 7) - 10 * np.cos(2 * np.pi * np.arange(days) / 7)
        
        # Monthly seasonality (fashion cycles)
        monthly_pattern = 30 * np.sin(2 * np.pi * np.arange(days) / 30.5)
        
        # Quarterly trend (seasonal fashion)
        quarterly_pattern = 40 * np.sin(2 * np.pi * np.arange(days) / 91.25)
        
        # Add trend (growing business)
        trend = np.arange(days) * 0.1
        
        # Random noise
        noise = np.random.normal(0, 15, days)
        
        # Occasional spikes (promotions, rush orders)
        spikes = np.random.poisson(0.05, days) * np.random.exponential(50, days)
        
        # Combine all components
        demand = (
            base_demand + 
            weekly_pattern + 
            monthly_pattern + 
            quarterly_pattern + 
            trend + 
            noise + 
            spikes
        )
        
        # Ensure non-negative demand
        demand = np.maximum(demand, 10)
        
        # Create DataFrame
        df = pd.DataFrame({
            'demand': demand
        }, index=dates)
        
        logger.info(f"Generated synthetic data: {len(df)} days, mean demand: {demand.mean():.1f}")
        
        return df
    
    def train_all_models(self, data: Optional[pd.DataFrame] = None, 
                        validation_split: float = 0.2) -> Dict[str, Dict[str, float]]:
        """Train all forecasting models"""
        
        if data is None:
            data = self.load_training_data()
        
        if data.empty:
            logger.error("No training data available")
            return {}
        
        logger.info(f"Training models with {len(data)} samples")
        
        # Split data for validation
        split_idx = int(len(data) * (1 - validation_split))
        train_data = data.iloc[:split_idx]
        val_data = data.iloc[split_idx:]
        
        logger.info(f"Train samples: {len(train_data)}, Validation samples: {len(val_data)}")
        
        results = {}
        
        # Train Prophet
        logger.info("Training Prophet model...")
        try:
            prophet_metrics = self.prophet_model.train(train_data, target_col='demand')
            results['prophet'] = prophet_metrics
            
            # Save model
            prophet_path = self.models_dir / 'prophet_model.joblib'
            self.prophet_model.save_model(prophet_path)
            
        except Exception as e:
            logger.error(f"Prophet training failed: {e}")
            results['prophet'] = {'error': str(e)}
        
        # Train XGBoost
        logger.info("Training XGBoost model...")
        try:
            xgboost_metrics = self.xgboost_model.train(train_data, target_col='demand')
            results['xgboost'] = xgboost_metrics
            
            # Save model
            xgboost_path = self.models_dir / 'xgboost_model.joblib'
            self.xgboost_model.save_model(xgboost_path)
            
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}")
            results['xgboost'] = {'error': str(e)}
        
        # Train LightGBM
        logger.info("Training LightGBM model...")
        try:
            lightgbm_metrics = self.lightgbm_model.train(train_data, target_col='demand')
            results['lightgbm'] = lightgbm_metrics
            
            # Save model
            lightgbm_path = self.models_dir / 'lightgbm_model.joblib'
            self.lightgbm_model.save_model(lightgbm_path)
            
        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")
            results['lightgbm'] = {'error': str(e)}
        
        # Evaluate models on validation data if available
        if len(val_data) > 7:
            logger.info("Evaluating models on validation data...")
            validation_results = self._evaluate_on_validation(val_data, horizon_days=len(val_data))
            
            # Merge validation results
            for model_name, val_metrics in validation_results.items():
                if model_name in results and 'error' not in results[model_name]:
                    results[model_name].update({f'val_{k}': v for k, v in val_metrics.items()})
        
        self.training_results = results
        
        # Save training summary
        self._save_training_summary(results, data)
        
        logger.info("Model training completed!")
        return results
    
    def _evaluate_on_validation(self, val_data: pd.DataFrame, horizon_days: int) -> Dict[str, Dict[str, float]]:
        """Evaluate trained models on validation data"""
        
        results = {}
        
        # Get last few days before validation for context
        context_data = val_data.iloc[:-horizon_days] if len(val_data) > horizon_days else val_data.iloc[:1]
        actual_values = val_data.iloc[-horizon_days:]['demand'].values
        
        # Evaluate Prophet
        if self.prophet_model.is_trained:
            try:
                prophet_pred, prophet_conf = self.prophet_model.predict(horizon_days)
                results['prophet'] = self.evaluator.calculate_metrics(
                    actual_values, prophet_pred, prophet_conf
                )
            except Exception as e:
                logger.warning(f"Prophet validation failed: {e}")
        
        # Evaluate XGBoost
        if self.xgboost_model.is_trained:
            try:
                xgb_pred, xgb_conf = self.xgboost_model.predict(
                    horizon_days, last_known_values=context_data
                )
                results['xgboost'] = self.evaluator.calculate_metrics(
                    actual_values, xgb_pred, xgb_conf
                )
            except Exception as e:
                logger.warning(f"XGBoost validation failed: {e}")
        
        # Evaluate LightGBM
        if self.lightgbm_model.is_trained:
            try:
                lgb_pred, lgb_conf = self.lightgbm_model.predict(
                    horizon_days, last_known_values=context_data
                )
                results['lightgbm'] = self.evaluator.calculate_metrics(
                    actual_values, lgb_pred, lgb_conf
                )
            except Exception as e:
                logger.warning(f"LightGBM validation failed: {e}")
        
        return results
    
    def _save_training_summary(self, results: Dict[str, Dict], data: pd.DataFrame):
        """Save comprehensive training summary"""
        
        summary = {
            'training_timestamp': datetime.now().isoformat(),
            'data_info': {
                'total_samples': len(data),
                'date_range': {
                    'start': data.index.min().isoformat() if hasattr(data.index, 'min') else None,
                    'end': data.index.max().isoformat() if hasattr(data.index, 'max') else None
                },
                'mean_demand': float(data['demand'].mean()),
                'std_demand': float(data['demand'].std()),
                'min_demand': float(data['demand'].min()),
                'max_demand': float(data['demand'].max())
            },
            'model_results': results,
            'best_models': self._identify_best_models(results),
            'recommendations': self._generate_recommendations(results, data)
        }
        
        # Save to JSON
        summary_path = self.models_dir / 'training_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Training summary saved to {summary_path}")
    
    def _identify_best_models(self, results: Dict[str, Dict]) -> Dict[str, str]:
        """Identify best performing models by metric"""
        
        best_models = {}
        
        # Models without errors
        valid_models = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_models:
            return {}
        
        # Best by RMSE (lower is better)
        if any('rmse' in v for v in valid_models.values()):
            rmse_scores = {k: v.get('rmse', float('inf')) for k, v in valid_models.items()}
            best_models['lowest_rmse'] = min(rmse_scores, key=rmse_scores.get)
        
        # Best by MAPE (lower is better)
        if any('mape' in v for v in valid_models.values()):
            mape_scores = {k: v.get('mape', float('inf')) for k, v in valid_models.items()}
            best_models['lowest_mape'] = min(mape_scores, key=mape_scores.get)
        
        # Best by validation RMSE if available
        val_rmse_scores = {k: v.get('val_rmse', float('inf')) for k, v in valid_models.items() 
                          if 'val_rmse' in v}
        if val_rmse_scores:
            best_models['best_validation'] = min(val_rmse_scores, key=val_rmse_scores.get)
        
        return best_models
    
    def _generate_recommendations(self, results: Dict[str, Dict], data: pd.DataFrame) -> List[str]:
        """Generate training recommendations"""
        
        recommendations = []
        
        # Check data quality
        if len(data) < 90:
            recommendations.append("Consider collecting more historical data (minimum 90 days recommended)")
        
        if data['demand'].std() / data['demand'].mean() > 1.0:
            recommendations.append("High demand variability detected - consider additional external features")
        
        # Model-specific recommendations
        valid_models = [k for k, v in results.items() if 'error' not in v]
        
        if 'prophet' not in valid_models:
            recommendations.append("Install Prophet for better seasonality handling: pip install prophet")
        
        if 'xgboost' not in valid_models:
            recommendations.append("Install XGBoost for non-linear pattern detection: pip install xgboost")
        
        if 'lightgbm' not in valid_models:
            recommendations.append("Install LightGBM for efficient gradient boosting: pip install lightgbm")
        
        # Performance recommendations
        if valid_models:
            avg_mape = np.mean([v.get('mape', 0) for v in results.values() if 'mape' in v])
            if avg_mape > 20:
                recommendations.append("Consider adding external features (weather, promotions, holidays)")
            elif avg_mape > 15:
                recommendations.append("Good performance - consider ensemble methods for improvement")
            else:
                recommendations.append("Excellent model performance achieved!")
        
        return recommendations
    
    def load_trained_models(self) -> Tuple[bool, Dict[str, bool]]:
        """Load previously trained models"""
        
        load_status = {}
        
        # Load Prophet
        prophet_path = self.models_dir / 'prophet_model.joblib'
        if prophet_path.exists():
            load_status['prophet'] = self.prophet_model.load_model(prophet_path)
        else:
            load_status['prophet'] = False
        
        # Load XGBoost
        xgboost_path = self.models_dir / 'xgboost_model.joblib'
        if xgboost_path.exists():
            load_status['xgboost'] = self.xgboost_model.load_model(xgboost_path)
        else:
            load_status['xgboost'] = False
        
        # Load LightGBM
        lightgbm_path = self.models_dir / 'lightgbm_model.joblib'
        if lightgbm_path.exists():
            load_status['lightgbm'] = self.lightgbm_model.load_model(lightgbm_path)
        else:
            load_status['lightgbm'] = False
        
        all_loaded = all(load_status.values())
        logger.info(f"Model loading status: {load_status}")
        
        return all_loaded, load_status
    
    def get_trained_models(self) -> Dict[str, Any]:
        """Get access to trained models"""
        
        models = {}
        
        if self.prophet_model.is_trained:
            models['prophet'] = self.prophet_model
        
        if self.xgboost_model.is_trained:
            models['xgboost'] = self.xgboost_model
            
        if self.lightgbm_model.is_trained:
            models['lightgbm'] = self.lightgbm_model
        
        return models
    
    def retrain_if_needed(self, data: Optional[pd.DataFrame] = None, 
                         max_age_days: int = 30) -> bool:
        """Check if models need retraining and retrain if necessary"""
        
        summary_path = self.models_dir / 'training_summary.json'
        
        if not summary_path.exists():
            logger.info("No previous training found, training new models")
            self.train_all_models(data)
            return True
        
        # Check age of last training
        try:
            with open(summary_path, 'r') as f:
                summary = json.load(f)
            
            last_training = pd.to_datetime(summary['training_timestamp'])
            age_days = (datetime.now() - last_training).days
            
            if age_days > max_age_days:
                logger.info(f"Models are {age_days} days old, retraining...")
                self.train_all_models(data)
                return True
            else:
                logger.info(f"Models are {age_days} days old, loading existing models")
                self.load_trained_models()
                return False
                
        except Exception as e:
            logger.error(f"Error checking training age: {e}")
            self.train_all_models(data)
            return True