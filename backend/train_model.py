import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib
import json

print("="*70)
print("🎯 HEARING DISABILITY PREDICTION MODEL TRAINING")
print("="*70)

# Load the data
df = pd.read_csv('game_analytics/game_analytics.csv')
print(f"\n📊 Loaded {len(df)} records from {df['session_id'].nunique()} unique sessions")

# Feature Engineering - Aggregate by session
def create_session_features(df):
    session_stats = []
    
    for session_id in df['session_id'].unique():
        session_data = df[df['session_id'] == session_id]
        
        response_times = session_data['response_time_ms'].values
        correct_answers = session_data['is_correct'].values
        
        # Calculate features
        features = {
            'session_id': session_id,
            'avg_response_time': np.mean(response_times),
            'median_response_time': np.median(response_times),
            'std_response_time': np.std(response_times),
            'max_response_time': np.max(response_times),
            'min_response_time': np.min(response_times),
            'response_time_range': np.max(response_times) - np.min(response_times),
            'slow_response_count': np.sum(response_times > 6000),
            'very_slow_count': np.sum(response_times > 10000),
            'slow_response_pct': np.sum(response_times > 6000) / len(response_times),
            'accuracy_rate': np.mean(correct_answers),
            'total_attempts': len(response_times),
            'incorrect_count': np.sum(~correct_answers),
            'has_hearing_disability': session_data['has_hearing_disability'].iloc[0]
        }
        session_stats.append(features)
    
    return pd.DataFrame(session_stats)

# Create features
print("\n🔧 Engineering features from session data...")
features_df = create_session_features(df)

print(f"   ✓ Created {len(features_df)} session-level feature sets")
print(f"   ✓ Sessions with disability: {features_df['has_hearing_disability'].sum()}")
print(f"   ✓ Sessions without disability: {(~features_df['has_hearing_disability']).sum()}")

# Prepare features and target
feature_columns = [
    'avg_response_time', 'median_response_time', 'std_response_time',
    'max_response_time', 'min_response_time', 'response_time_range',
    'slow_response_count', 'very_slow_count', 'slow_response_pct',
    'accuracy_rate', 'total_attempts', 'incorrect_count'
]

X = features_df[feature_columns]
y = features_df['has_hearing_disability']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\n📈 Training set: {len(X_train)} sessions")
print(f"   - With disability: {y_train.sum()}")
print(f"   - Without disability: {(~y_train).sum()}")
print(f"📉 Test set: {len(X_test)} sessions")
print(f"   - With disability: {y_test.sum()}")
print(f"   - Without disability: {(~y_test).sum()}")

# Train Random Forest Model
print("\n🌲 Training Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    class_weight='balanced'
)

rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)
y_proba = rf_model.predict_proba(X_test)[:, 1]

# Evaluate model
print("\n" + "="*70)
print("📊 MODEL PERFORMANCE")
print("="*70)

accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, 
                          target_names=['No Disability', 'Has Disability'],
                          digits=3))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"   True Negatives:  {cm[0][0]}")
print(f"   False Positives: {cm[0][1]}")
print(f"   False Negatives: {cm[1][0]}")
print(f"   True Positives:  {cm[1][1]}")

try:
    roc_score = roc_auc_score(y_test, y_proba)
    print(f"\nROC-AUC Score: {roc_score:.3f}")
except:
    print("\nROC-AUC Score: N/A (need more diverse test data)")

# Feature Importance
print("\n" + "="*70)
print("🔍 FEATURE IMPORTANCE")
print("="*70)
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    bar = '█' * int(row['importance'] * 100)
    print(f"{row['feature']:25s} {bar} {row['importance']:.4f}")

# Cross-validation
print("\n" + "="*70)
print("✅ CROSS-VALIDATION (5-Fold)")
print("="*70)
cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

# Save model and configuration
print("\n" + "="*70)
print("💾 SAVING MODEL")
print("="*70)

model_config = {
    'feature_columns': feature_columns,
    'threshold_probability': 0.5,
    'min_attempts_for_prediction': 5,
    'version': '1.0',
    'training_date': pd.Timestamp.now().isoformat(),
    'training_samples': len(X_train),
    'test_accuracy': float(accuracy),
    'feature_importance': feature_importance.to_dict('records')
}

joblib.dump(rf_model, 'hearing_model.pkl')
with open('model_config.json', 'w') as f:
    json.dump(model_config, f, indent=2)

print("✓ Model saved: hearing_model.pkl")
print("✓ Config saved: model_config.json")

# Test predictions
print("\n" + "="*70)
print("🔮 EXAMPLE PREDICTIONS")
print("="*70)

examples = [
    {
        'name': 'Normal Child (Fast & Accurate)',
        'avg_response_time': 3200,
        'median_response_time': 3100,
        'std_response_time': 600,
        'max_response_time': 5000,
        'min_response_time': 2400,
        'response_time_range': 2600,
        'slow_response_count': 0,
        'very_slow_count': 0,
        'slow_response_pct': 0.0,
        'accuracy_rate': 0.85,
        'total_attempts': 20,
        'incorrect_count': 3
    },
    {
        'name': 'Child with Potential Disability (Slow)',
        'avg_response_time': 9000,
        'median_response_time': 8500,
        'std_response_time': 2500,
        'max_response_time': 15000,
        'min_response_time': 6000,
        'response_time_range': 9000,
        'slow_response_count': 18,
        'very_slow_count': 10,
        'slow_response_pct': 0.90,
        'accuracy_rate': 0.60,
        'total_attempts': 20,
        'incorrect_count': 8
    }
]

for example in examples:
    name = example.pop('name')
    example_df = pd.DataFrame([example])
    
    prediction = rf_model.predict(example_df)[0]
    probability = rf_model.predict_proba(example_df)[0]
    
    print(f"\n{name}:")
    print(f"  Avg Response Time: {example['avg_response_time']}ms")
    print(f"  Slow Responses: {example['slow_response_count']}/{example['total_attempts']}")
    print(f"  Accuracy: {example['accuracy_rate']*100:.0f}%")
    print(f"  → Prediction: {'⚠️  HAS hearing disability' if prediction else '✅ NO hearing disability'}")
    print(f"  → Confidence: {probability[1]*100:.1f}% disability | {probability[0]*100:.1f}% normal")

print("\n" + "="*70)
print("✅ MODEL TRAINING COMPLETE!")
print("="*70)
