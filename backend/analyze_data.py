import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class GameAnalytics:
    """Analyze game data for ML insights"""
    
    def __init__(self, data_dir='game_analytics'):
        self.data_dir = data_dir
        self.csv_file = os.path.join(data_dir, 'game_analytics.csv')
        self.json_file = os.path.join(data_dir, 'game_logs.json')
        self.df = None
        
    def load_data(self):
        """Load data from CSV file"""
        if not os.path.exists(self.csv_file):
            print(f"No data file found at {self.csv_file}")
            return None
        
        self.df = pd.read_csv(self.csv_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        print(f"Loaded {len(self.df)} records")
        return self.df
    
    def basic_statistics(self):
        """Calculate basic statistics"""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return
        
        print("\n=== BASIC STATISTICS ===")
        print(f"Total interactions: {len(self.df)}")
        print(f"Unique sessions: {self.df['session_id'].nunique()}")
        print(f"Correct attempts: {self.df['is_correct'].sum()}")
        print(f"Incorrect attempts: {(~self.df['is_correct']).sum()}")
        print(f"Overall accuracy: {self.df['is_correct'].mean() * 100:.2f}%")
        print(f"\nAverage response time: {self.df['response_time_ms'].mean():.2f} ms")
        print(f"Median response time: {self.df['response_time_ms'].median():.2f} ms")
        print(f"Min response time: {self.df['response_time_ms'].min():.2f} ms")
        print(f"Max response time: {self.df['response_time_ms'].max():.2f} ms")
        
    def animal_performance(self):
        """Analyze performance by animal"""
        if self.df is None:
            return
        
        print("\n=== PERFORMANCE BY ANIMAL ===")
        animal_stats = self.df.groupby('animal_shown').agg({
            'is_correct': ['count', 'sum', 'mean'],
            'response_time_ms': ['mean', 'median']
        }).round(2)
        
        animal_stats.columns = ['Total', 'Correct', 'Accuracy', 'Avg_Response_ms', 'Median_Response_ms']
        animal_stats['Accuracy'] = animal_stats['Accuracy'] * 100
        print(animal_stats)
        
        return animal_stats
    
    def confusion_matrix_analysis(self):
        """Create confusion matrix of animal selections"""
        if self.df is None:
            return
        
        print("\n=== CONFUSION MATRIX ===")
        confusion = pd.crosstab(
            self.df['animal_shown'], 
            self.df['animal_selected'],
            normalize='index'
        ) * 100
        print(confusion.round(2))
        
        return confusion
    
    def response_time_distribution(self):
        """Analyze response time distribution"""
        if self.df is None:
            return
        
        plt.figure(figsize=(14, 6))
        
        # Overall distribution
        plt.subplot(1, 2, 1)
        plt.hist(self.df['response_time_ms'], bins=30, edgecolor='black', alpha=0.7)
        plt.axvline(self.df['response_time_ms'].mean(), color='red', 
                   linestyle='--', label=f'Mean: {self.df["response_time_ms"].mean():.0f}ms')
        plt.axvline(self.df['response_time_ms'].median(), color='green', 
                   linestyle='--', label=f'Median: {self.df["response_time_ms"].median():.0f}ms')
        plt.xlabel('Response Time (ms)')
        plt.ylabel('Frequency')
        plt.title('Response Time Distribution')
        plt.legend()
        
        # Correct vs Incorrect
        plt.subplot(1, 2, 2)
        correct = self.df[self.df['is_correct']]['response_time_ms']
        incorrect = self.df[~self.df['is_correct']]['response_time_ms']
        
        plt.hist([correct, incorrect], bins=20, label=['Correct', 'Incorrect'], 
                alpha=0.7, edgecolor='black')
        plt.xlabel('Response Time (ms)')
        plt.ylabel('Frequency')
        plt.title('Response Time: Correct vs Incorrect')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.data_dir, 'response_time_analysis.png'), dpi=300)
        print(f"Saved plot to {os.path.join(self.data_dir, 'response_time_analysis.png')}")
        plt.show()
    
    def learning_curve(self):
        """Analyze learning progression over attempts"""
        if self.df is None:
            return
        
        # Group by attempt number
        learning = self.df.groupby('attempt_number').agg({
            'is_correct': 'mean',
            'response_time_ms': 'mean'
        }).reset_index()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Accuracy over attempts
        ax1.plot(learning['attempt_number'], learning['is_correct'] * 100, 
                marker='o', linewidth=2)
        ax1.set_xlabel('Attempt Number')
        ax1.set_ylabel('Accuracy (%)')
        ax1.set_title('Learning Curve: Accuracy Over Attempts')
        ax1.grid(True, alpha=0.3)
        
        # Response time over attempts
        ax2.plot(learning['attempt_number'], learning['response_time_ms'], 
                marker='s', linewidth=2, color='orange')
        ax2.set_xlabel('Attempt Number')
        ax2.set_ylabel('Average Response Time (ms)')
        ax2.set_title('Response Time Improvement Over Attempts')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.data_dir, 'learning_curve.png'), dpi=300)
        print(f"Saved plot to {os.path.join(self.data_dir, 'learning_curve.png')}")
        plt.show()
    
    def session_analysis(self):
        """Analyze individual sessions"""
        if self.df is None:
            return
        
        print("\n=== SESSION ANALYSIS ===")
        session_stats = self.df.groupby('session_id').agg({
            'is_correct': ['count', 'sum', 'mean'],
            'response_time_ms': 'mean',
            'game_duration_sec': 'max'
        }).round(2)
        
        session_stats.columns = ['Total_Attempts', 'Correct', 'Accuracy', 
                                 'Avg_Response_ms', 'Duration_sec']
        session_stats['Accuracy'] = session_stats['Accuracy'] * 100
        
        print(session_stats)
        return session_stats
    
    def export_for_ml(self, output_file='ml_features.csv'):
        """Export processed features for ML models"""
        if self.df is None:
            return
        
        # Create ML-ready features
        ml_data = self.df.copy()
        
        # Add time-based features
        ml_data['hour'] = ml_data['timestamp'].dt.hour
        ml_data['day_of_week'] = ml_data['timestamp'].dt.dayofweek
        
        # Add rolling features (if multiple attempts)
        ml_data = ml_data.sort_values(['session_id', 'attempt_number'])
        ml_data['prev_correct'] = ml_data.groupby('session_id')['is_correct'].shift(1)
        ml_data['prev_response_time'] = ml_data.groupby('session_id')['response_time_ms'].shift(1)
        
        # One-hot encode animals
        ml_data = pd.get_dummies(ml_data, columns=['animal_shown', 'animal_selected'], 
                                 prefix=['shown', 'selected'])
        
        output_path = os.path.join(self.data_dir, output_file)
        ml_data.to_csv(output_path, index=False)
        print(f"\n=== ML FEATURES EXPORTED ===")
        print(f"Saved to: {output_path}")
        print(f"Features: {list(ml_data.columns)}")
        print(f"Shape: {ml_data.shape}")
        
        return ml_data
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("=" * 60)
        print("ANIMAL SOUNDS GAME - ANALYTICS REPORT")
        print("=" * 60)
        
        self.basic_statistics()
        self.animal_performance()
        self.confusion_matrix_analysis()
        self.session_analysis()
        
        # Generate visualizations
        print("\n=== GENERATING VISUALIZATIONS ===")
        self.response_time_distribution()
        self.learning_curve()
        
        # Export for ML
        self.export_for_ml()
        
        print("\n" + "=" * 60)
        print("REPORT COMPLETE")
        print("=" * 60)


def main():
    """Main execution function"""
    analyzer = GameAnalytics()
    
    # Load data
    df = analyzer.load_data()
    
    if df is not None and len(df) > 0:
        # Generate full report
        analyzer.generate_report()
    else:
        print("No data available for analysis yet.")
        print("Play the game to generate data!")


if __name__ == "__main__":
    main()