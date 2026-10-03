# Experiment 2 Results

## Environment and data
- Dataset: Iris, 150 samples, 4 features, 3 classes.
- Split: 70% training / 30% test, `random_state=42`, `stratify=y`.
- Training shape: (105, 4); test shape: (45, 4).

## Required results
- Best test accuracy among k = 1, 3, 5, 7, 9, 11: k=5, accuracy=0.9778.
- KNN k=5 confusion matrix (rows=true, columns=predicted):

```text
[[15  0  0]
 [ 0 15  0]
 [ 0  1 14]]
```

- KNN k=5 classification report:

```text
              precision    recall  f1-score   support

      setosa     1.0000    1.0000    1.0000        15
  versicolor     0.9375    1.0000    0.9677        15
   virginica     1.0000    0.9333    0.9655        15

    accuracy                         0.9778        45
   macro avg     0.9792    0.9778    0.9778        45
weighted avg     0.9792    0.9778    0.9778        45

```

## Interpretation points
- k=1 usually has low bias but is more sensitive to individual samples and noise.
- Larger k values smooth the decision boundary and can underfit if k is too large.
- A deep decision tree can reach very high training accuracy while its test accuracy does not improve, which is a sign of overfitting.
- KNN depends on distance, so feature scaling is important when feature ranges differ.

## Generated files
- `knn_k_comparison.csv`
- `decision_tree_depth_comparison.csv`
- `confusion_matrix.txt`
- `classification_report.txt`
- `random_state_comparison.csv`
- `stratify_class_counts.csv`
- `scaling_comparison.csv`
- `cross_validation.csv`
- `knn_decision_boundary.png`
