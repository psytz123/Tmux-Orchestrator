"""
Model Evaluation and Performance Metrics
Comprehensive evaluation framework for forecasting models
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

try:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available for advanced metrics")

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive evaluation of forecasting models"""
    
    def __init__(self):
        self.evaluation_history = []
        
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                         confidence: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate comprehensive forecasting metrics"""
        
        # Convert to numpy arrays
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        if len(y_true) != len(y_pred):
            logger.error(f"Mismatched lengths: true={len(y_true)}, pred={len(y_pred)}")
            return {"error": "length_mismatch"}
        
        if len(y_true) == 0:
            return {"error": "empty_data"}
        
        try:
            metrics = {}
            
            # Basic metrics
            metrics['mae'] = float(mean_absolute_error(y_true, y_pred))
            metrics['rmse'] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
            
            # Mean Absolute Percentage Error
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
            metrics['mape'] = float(mape)
            
            # Symmetric MAPE (handles zero values better)
            smape = 2.0 * np.mean(np.abs(y_pred - y_true) / (np.abs(y_pred) + np.abs(y_true) + 1e-8)) * 100
            metrics['smape'] = float(smape)
            
            # Mean Absolute Scaled Error (MASE)
            if len(y_true) > 1:
                naive_mae = np.mean(np.abs(np.diff(y_true)))
                metrics['mase'] = float(metrics['mae'] / (naive_mae + 1e-8))
            
            # R-squared
            if SKLEARN_AVAILABLE:
                metrics['r2'] = float(r2_score(y_true, y_pred))
            
            # Bias metrics
            bias = np.mean(y_pred - y_true)
            metrics['bias'] = float(bias)
            metrics['bias_percent'] = float(bias / (np.mean(y_true) + 1e-8) * 100)
            
            # Accuracy metrics
            accuracy = 100 - mape
            metrics['accuracy'] = float(max(0, accuracy))
            
            # Directional accuracy (for trending)
            if len(y_true) > 1:
                true_direction = np.diff(y_true) > 0
                pred_direction = np.diff(y_pred) > 0
                dir_accuracy = np.mean(true_direction == pred_direction) * 100
                metrics['directional_accuracy'] = float(dir_accuracy)
            
            # Confidence-based metrics
            if confidence is not None and len(confidence) == len(y_true):
                # Coverage probability (are actual values within confidence intervals?)
                errors = np.abs(y_true - y_pred)
                within_confidence = errors <= confidence * np.abs(y_pred)
                metrics['confidence_coverage'] = float(np.mean(within_confidence) * 100)
                
                # Confidence calibration (correlation between confidence and actual error)
                if np.std(confidence) > 0:
                    confidence_corr = np.corrcoef(confidence, errors)[0, 1]
                    metrics['confidence_calibration'] = float(confidence_corr)
            
            # Percentile errors
            abs_errors = np.abs(y_true - y_pred)
            metrics['p50_error'] = float(np.percentile(abs_errors, 50))
            metrics['p90_error'] = float(np.percentile(abs_errors, 90))
            metrics['p95_error'] = float(np.percentile(abs_errors, 95))
            
            # Residual analysis
            residuals = y_true - y_pred
            metrics['residual_mean'] = float(np.mean(residuals))
            metrics['residual_std'] = float(np.std(residuals))
            metrics['residual_skewness'] = float(self._calculate_skewness(residuals))
            
            # Peak detection accuracy (important for demand planning)
            if len(y_true) > 5:
                true_peaks = self._find_peaks(y_true)
                pred_peaks = self._find_peaks(y_pred)
                peak_accuracy = self._peak_matching_accuracy(true_peaks, pred_peaks)
                metrics['peak_detection_accuracy'] = float(peak_accuracy)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        if len(data) < 3:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        if std == 0:
            return 0.0
        
        skew = np.mean(((data - mean) / std) ** 3)
        return skew
    
    def _find_peaks(self, data: np.ndarray, min_prominence: float = None) -> List[int]:
        """Find peaks in time series data"""
        if min_prominence is None:
            min_prominence = np.std(data) * 0.5
        
        peaks = []
        for i in range(1, len(data) - 1):
            if (data[i] > data[i-1] and data[i] > data[i+1] and 
                data[i] > np.mean(data) + min_prominence):
                peaks.append(i)
        
        return peaks
    
    def _peak_matching_accuracy(self, true_peaks: List[int], pred_peaks: List[int], 
                               tolerance: int = 2) -> float:
        """Calculate accuracy of peak detection with tolerance window"""
        if not true_peaks:
            return 100.0 if not pred_peaks else 0.0
        
        if not pred_peaks:
            return 0.0
        
        matches = 0
        for true_peak in true_peaks:
            # Check if any predicted peak is within tolerance
            for pred_peak in pred_peaks:
                if abs(true_peak - pred_peak) <= tolerance:
                    matches += 1
                    break
        
        accuracy = matches / len(true_peaks) * 100
        return accuracy
    
    def time_series_cross_validation(self, model, data: pd.DataFrame, 
                                   initial_train_size: int = 60,
                                   step_size: int = 7,
                                   horizon: int = 7,
                                   max_folds: int = 10) -> Dict[str, Any]:
        """Perform time series cross-validation"""
        
        if len(data) < initial_train_size + horizon:
            logger.warning("Insufficient data for time series CV")
            return {"error": "insufficient_data"}
        
        cv_results = []
        fold_metrics = []
        
        current_train_end = initial_train_size
        fold = 0
        
        while (current_train_end + horizon <= len(data) and fold < max_folds):
            try:
                # Split data
                train_data = data.iloc[:current_train_end]
                test_data = data.iloc[current_train_end:current_train_end + horizon]
                
                # Train model on fold
                model_copy = type(model)()  # Create new instance
                train_metrics = model_copy.train(train_data, target_col='demand')
                
                if 'error' in train_metrics:
                    logger.warning(f"Training failed on fold {fold}")
                    current_train_end += step_size
                    fold += 1
                    continue
                
                # Make predictions
                if hasattr(model_copy, 'predict'):
                    predictions, confidence = model_copy.predict(
                        horizon, last_known_values=train_data
                    )
                    
                    # Calculate metrics
                    actual = test_data['demand'].values
                    fold_metric = self.calculate_metrics(actual, predictions, confidence)
                    
                    fold_results = {
                        'fold': fold,
                        'train_size': len(train_data),
                        'test_size': len(test_data),
                        'train_end': train_data.index[-1] if hasattr(train_data.index, '__getitem__') else None,
                        'test_start': test_data.index[0] if hasattr(test_data.index, '__getitem__') else None,
                        'metrics': fold_metric
                    }
                    
                    cv_results.append(fold_results)
                    fold_metrics.append(fold_metric)
                
            except Exception as e:
                logger.warning(f"Error in CV fold {fold}: {e}")
            
            current_train_end += step_size
            fold += 1
        
        if not fold_metrics:
            return {"error": "no_successful_folds"}
        
        # Aggregate results
        aggregated_metrics = self._aggregate_cv_metrics(fold_metrics)
        
        return {
            'fold_count': len(cv_results),
            'aggregated_metrics': aggregated_metrics,
            'fold_details': cv_results,
            'stability_metrics': self._calculate_stability_metrics(fold_metrics)
        }
    
    def _aggregate_cv_metrics(self, fold_metrics: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Aggregate cross-validation metrics across folds"""
        
        aggregated = {}
        
        # Get all metric keys
        all_keys = set()
        for fold in fold_metrics:
            if 'error' not in fold:
                all_keys.update(fold.keys())
        
        for key in all_keys:
            values = [fold[key] for fold in fold_metrics if key in fold and 'error' not in fold]
            
            if values:
                aggregated[key] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }
        
        return aggregated
    
    def _calculate_stability_metrics(self, fold_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate stability metrics across CV folds"""
        
        stability = {}
        
        key_metrics = ['mae', 'rmse', 'mape', 'accuracy']
        
        for metric in key_metrics:
            values = [fold[metric] for fold in fold_metrics if metric in fold and 'error' not in fold]
            
            if len(values) > 1:
                cv_coeff = np.std(values) / (np.mean(values) + 1e-8)
                stability[f'{metric}_stability'] = float(1.0 / (1.0 + cv_coeff))  # Higher is more stable
        
        return stability
    
    def compare_models(self, model_results: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Compare performance of multiple models"""
        
        # Filter out models with errors
        valid_models = {k: v for k, v in model_results.items() if 'error' not in v}
        
        if len(valid_models) < 2:
            return {"error": "need_at_least_two_models"}
        
        comparison = {
            'model_rankings': {},
            'best_model_by_metric': {},
            'performance_summary': {},
            'recommendations': []
        }
        
        # Key metrics for comparison
        metrics_to_compare = ['mae', 'rmse', 'mape', 'accuracy', 'r2']
        
        # Rank models by each metric
        for metric in metrics_to_compare:
            if all(metric in model for model in valid_models.values()):
                # For accuracy and r2, higher is better
                reverse = metric in ['accuracy', 'r2']
                
                sorted_models = sorted(
                    valid_models.items(),
                    key=lambda x: x[1][metric],
                    reverse=reverse
                )
                
                comparison['model_rankings'][metric] = [
                    {'model': model, 'value': metrics[metric], 'rank': i+1}
                    for i, (model, metrics) in enumerate(sorted_models)
                ]
                
                comparison['best_model_by_metric'][metric] = sorted_models[0][0]
        
        # Overall performance summary
        model_scores = {}
        for model_name in valid_models.keys():
            score = 0
            count = 0
            
            for metric in metrics_to_compare:
                if metric in comparison['model_rankings']:
                    ranking = comparison['model_rankings'][metric]
                    for entry in ranking:
                        if entry['model'] == model_name:
                            # Convert rank to score (lower rank = higher score)
                            score += (len(valid_models) - entry['rank'] + 1)
                            count += 1
                            break
            
            if count > 0:
                model_scores[model_name] = score / count
        
        # Sort by overall score
        sorted_overall = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        comparison['overall_ranking'] = sorted_overall
        
        if sorted_overall:
            comparison['best_overall_model'] = sorted_overall[0][0]
        
        # Performance summary
        for model_name, metrics in valid_models.items():
            summary = {
                'strengths': [],
                'weaknesses': [],
                'overall_score': model_scores.get(model_name, 0)
            }
            
            # Identify strengths and weaknesses
            for metric in metrics_to_compare:
                if metric in comparison['best_model_by_metric']:
                    if comparison['best_model_by_metric'][metric] == model_name:
                        summary['strengths'].append(f"Best {metric}")
            
            # Add specific performance notes
            if metrics.get('mape', 100) < 10:
                summary['strengths'].append("Excellent accuracy (MAPE < 10%)")
            elif metrics.get('mape', 100) > 20:
                summary['weaknesses'].append("Poor accuracy (MAPE > 20%)")
            
            if metrics.get('bias_percent', 0) > 10:
                summary['weaknesses'].append("High positive bias")
            elif metrics.get('bias_percent', 0) < -10:
                summary['weaknesses'].append("High negative bias")
            
            comparison['performance_summary'][model_name] = summary
        
        # Generate recommendations
        if sorted_overall:
            best_model = sorted_overall[0][0]
            comparison['recommendations'].append(f"Recommended primary model: {best_model}")
            
            if len(sorted_overall) > 1:
                second_best = sorted_overall[1][0]
                comparison['recommendations'].append(f"Recommended secondary model: {second_best}")
                comparison['recommendations'].append("Consider ensemble approach combining top models")
        
        return comparison
    
    def generate_evaluation_report(self, model_name: str, metrics: Dict[str, float],
                                 save_path: Optional[str] = None) -> str:
        """Generate detailed evaluation report"""
        
        report_lines = [
            f"# Model Evaluation Report: {model_name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Performance Metrics",
            ""
        ]
        
        # Group metrics by category
        accuracy_metrics = ['mae', 'rmse', 'mape', 'smape', 'accuracy']
        bias_metrics = ['bias', 'bias_percent']
        advanced_metrics = ['r2', 'mase', 'directional_accuracy']
        
        def add_metric_section(title: str, metric_keys: List[str]):
            report_lines.append(f"### {title}")
            for key in metric_keys:
                if key in metrics:
                    value = metrics[key]
                    if key in ['mape', 'smape', 'accuracy', 'bias_percent', 'directional_accuracy']:
                        report_lines.append(f"- **{key.upper()}**: {value:.2f}%")
                    else:
                        report_lines.append(f"- **{key.upper()}**: {value:.4f}")
            report_lines.append("")
        
        add_metric_section("Accuracy Metrics", accuracy_metrics)
        add_metric_section("Bias Analysis", bias_metrics)
        add_metric_section("Advanced Metrics", advanced_metrics)
        
        # Performance assessment
        report_lines.extend([
            "## Performance Assessment",
            ""
        ])
        
        mape = metrics.get('mape', float('inf'))
        if mape < 5:
            assessment = "Excellent"
        elif mape < 10:
            assessment = "Very Good"
        elif mape < 15:
            assessment = "Good"
        elif mape < 25:
            assessment = "Fair"
        else:
            assessment = "Poor"
        
        report_lines.append(f"**Overall Performance**: {assessment} (MAPE: {mape:.2f}%)")
        
        # Recommendations
        recommendations = []
        if mape > 20:
            recommendations.append("Consider adding more features or external data sources")
        if metrics.get('bias_percent', 0) > 5:
            recommendations.append("Model shows systematic overestimation - consider bias correction")
        elif metrics.get('bias_percent', 0) < -5:
            recommendations.append("Model shows systematic underestimation - consider bias correction")
        
        if recommendations:
            report_lines.extend([
                "",
                "## Recommendations",
                ""
            ])
            for rec in recommendations:
                report_lines.append(f"- {rec}")
        
        report_content = "\n".join(report_lines)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_content)
            logger.info(f"Evaluation report saved to {save_path}")
        
        return report_content