"""
泰坦尼克号案例 - 模型训练与评估模块
Titanic Case - Model Training & Evaluation Module

支持多种模型: LogisticRegression, RandomForest, XGBoost, LightGBM, SVM, KNN
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Optional

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
    GridSearchCV,
    RandomizedSearchCV,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    classification_report,
    confusion_matrix,
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    StackingClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import warnings
warnings.filterwarnings("ignore")


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple:
    """
    划分训练集和验证集
    
    Args:
        X: 特征DataFrame
        y: 目标变量
        test_size: 验证集比例
        random_state: 随机种子
        
    Returns:
        (X_train, X_val, y_train, y_val)
    """
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    print(f"数据划分: 训练集 {X_train.shape[0]} 样本, 验证集 {X_val.shape[0]} 样本")
    return X_train, X_val, y_train, y_val


def get_default_models() -> Dict:
    """
    获取默认模型配置
    
    Returns:
        模型字典
    """
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "KNN": KNeighborsClassifier(),
        "SVM": SVC(probability=True, random_state=42),
    }


def evaluate_models(
    models: Dict,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> pd.DataFrame:
    """
    评估多个模型的性能
    
    Args:
        models: 模型字典
        X_train: 训练特征
        y_train: 训练目标
        X_val: 验证特征
        y_val: 验证目标
        
    Returns:
        评估结果DataFrame
    """
    results = []
    
    for name, model in models.items():
        print(f"\n{'='*40}")
        print(f"  训练模型: {name}")
        print(f"{'='*40}")
        
        # 训练
        model.fit(X_train, y_train)
        
        # 预测
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        
        # 计算指标
        metrics = {
            "Model": name,
            "Train_Accuracy": accuracy_score(y_train, y_train_pred),
            "Val_Accuracy": accuracy_score(y_val, y_val_pred),
            "Val_Precision": precision_score(y_val, y_val_pred),
            "Val_Recall": recall_score(y_val, y_val_pred),
            "Val_F1": f1_score(y_val, y_val_pred),
        }
        
        # 尝试计算 AUC
        try:
            y_val_prob = model.predict_proba(X_val)[:, 1]
            metrics["Val_AUC"] = roc_auc_score(y_val, y_val_prob)
        except (AttributeError, IndexError):
            metrics["Val_AUC"] = None
        
        results.append(metrics)
        
        # 打印详细报告
        print(f"\n  训练集准确率: {metrics['Train_Accuracy']:.4f}")
        print(f"  验证集准确率: {metrics['Val_Accuracy']:.4f}")
        print(f"  验证集 F1: {metrics['Val_F1']:.4f}")
        
        if metrics["Val_AUC"]:
            print(f"  验证集 AUC: {metrics['Val_AUC']:.4f}")
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("Val_Accuracy", ascending=False)
    
    print(f"\n{'='*60}")
    print(f"  模型性能排名 (按验证集准确率)")
    print(f"{'='*60}")
    print(results_df.to_string(index=False))
    
    return results_df


def cross_validate_models(
    models: Dict,
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = 5
) -> pd.DataFrame:
    """
    交叉验证评估模型
    
    Args:
        models: 模型字典
        X: 全部特征
        y: 全部目标
        cv: 交叉验证折数
        
    Returns:
        交叉验证结果DataFrame
    """
    results = []
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    for name, model in models.items():
        print(f"\n  交叉验证: {name} ({cv}折)")
        
        scores = cross_val_score(model, X, y, cv=skf, scoring="accuracy")
        
        results.append({
            "Model": name,
            "CV_Accuracy_Mean": scores.mean(),
            "CV_Accuracy_Std": scores.std(),
            "CV_Accuracy_Min": scores.min(),
            "CV_Accuracy_Max": scores.max(),
        })
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("CV_Accuracy_Mean", ascending=False)
    
    print(f"\n【交叉验证结果 ({cv}折)】")
    for _, row in results_df.iterrows():
        print(f"  {row['Model']}: {row['CV_Accuracy_Mean']:.4f} ± {row['CV_Accuracy_Std']:.4f}")
    
    return results_df


def tune_hyperparameters(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: str = "random_forest"
) -> Tuple:
    """
    模型超参数调优
    
    Args:
        X: 特征
        y: 目标
        model_type: 模型类型
        
    Returns:
        (best_model, best_params, best_score)
    """
    print(f"\n{'='*60}")
    print(f"  超参数调优: {model_type}")
    print(f"{'='*60}")
    
    param_grids = {
        "logistic_regression": {
            "model": LogisticRegression(random_state=42),
            "params": {
                "C": [0.01, 0.1, 1, 10, 100],
                "max_iter": [500, 1000, 2000],
                "solver": ["lbfgs", "liblinear"],
            },
        },
        "random_forest": {
            "model": RandomForestClassifier(random_state=42),
            "params": {
                "n_estimators": [100, 200, 500],
                "max_depth": [5, 10, 15, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "criterion": ["gini", "entropy"],
            },
        },
        "gradient_boosting": {
            "model": GradientBoostingClassifier(random_state=42),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.05, 0.1],
                "min_samples_split": [2, 5, 10],
            },
        },
        "svm": {
            "model": SVC(probability=True, random_state=42),
            "params": {
                "C": [0.1, 1, 10],
                "kernel": ["rbf", "linear"],
                "gamma": ["scale", "auto"],
            },
        },
        "knn": {
            "model": KNeighborsClassifier(),
            "params": {
                "n_neighbors": [3, 5, 7, 9, 11],
                "weights": ["uniform", "distance"],
                "metric": ["euclidean", "manhattan"],
            },
        },
    }
    
    if model_type not in param_grids:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    config = param_grids[model_type]
    
    # 使用 RandomizedSearchCV 进行高效搜索
    search = RandomizedSearchCV(
        config["model"],
        config["params"],
        n_iter=50,
        cv=5,
        scoring="accuracy",
        random_state=42,
        n_jobs=-1,
    )
    
    search.fit(X, y)
    
    best_model = search.best_estimator_
    best_params = search.best_params_
    best_score = search.best_score_
    
    print(f"\n  最佳参数: {best_params}")
    print(f"  最佳分数: {best_score:.4f}")
    
    return best_model, best_params, best_score


def create_ensemble_model(
    best_models: Dict[str, object],
    voting: str = "soft"
) -> VotingClassifier:
    """
    创建投票集成模型
    
    Args:
        best_models: 最佳模型字典
        voting: 投票方式 ('soft' 或 'hard')
        
    Returns:
        VotingClassifier
    """
    estimators = list(best_models.items())
    
    ensemble = VotingClassifier(
        estimators=estimators,
        voting=voting,
        n_jobs=-1,
    )
    
    print(f"\n创建投票集成模型: {[name for name, _ in estimators]}")
    return ensemble


def plot_confusion_matrix_custom(
    y_true: pd.Series,
    y_pred: np.ndarray,
    model_name: str = "Model",
    save_path: Optional[str] = None
) -> None:
    """
    绘制混淆矩阵
    
    Args:
        y_true: 真实标签
        y_pred: 预测标签
        model_name: 模型名称
        save_path: 保存路径
    """
    cm = confusion_matrix(y_true, y_pred)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["Not Survived", "Survived"],
                yticklabels=["Not Survived", "Survived"])
    ax.set_title(f"Confusion Matrix - {model_name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.show()


def plot_roc_curves(
    models: Dict,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    save_path: Optional[str] = None
) -> None:
    """
    绘制多模型ROC曲线对比
    
    Args:
        models: 模型字典
        X_val: 验证特征
        y_val: 验证标签
        save_path: 保存路径
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for name, model in models.items():
        try:
            y_prob = model.predict_proba(X_val)[:, 1]
            fpr, tpr, _ = roc_curve(y_val, y_prob)
            auc = roc_auc_score(y_val, y_prob)
            ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
        except (AttributeError, IndexError):
            pass
    
    ax.plot([0, 1], [0, 1], "k--", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves Comparison")
    ax.legend(loc="lower right")
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.show()


def plot_feature_importance(
    model,
    feature_names: List[str],
    top_n: int = 20,
    save_path: Optional[str] = None
) -> None:
    """
    绘制特征重要性排名
    
    Args:
        model: 训练好的模型
        feature_names: 特征名列表
        top_n: 显示前N个重要特征
        save_path: 保存路径
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        print("该模型不支持特征重要性分析")
        return
    
    # 排序
    indices = np.argsort(importances)[::-1][:top_n]
    top_importances = importances[indices]
    top_features = [feature_names[i] for i in indices]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(top_n), top_importances[::-1])
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_features[::-1])
    ax.set_xlabel("Feature Importance")
    ax.set_title(f"Top {top_n} Feature Importances")
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.show()


def generate_submission(
    model,
    test_df: pd.DataFrame,
    passenger_ids: pd.Series,
    feature_cols: List[str],
    output_path: str
) -> str:
    """
    生成Kaggle提交文件
    
    Args:
        model: 训练好的模型
        test_df: 测试集特征
        passenger_ids: 乘客ID
        feature_cols: 使用的特征列
        output_path: 输出路径
        
    Returns:
        提交文件路径
    """
    # 确保特征列存在
    available_cols = [c for c in feature_cols if c in test_df.columns]
    X_test = test_df[available_cols]
    
    # 预测
    predictions = model.predict(X_test)
    
    # 创建提交文件
    submission = pd.DataFrame({
        "PassengerId": passenger_ids,
        "Survived": predictions,
    })
    
    # 转换为整数
    submission["Survived"] = submission["Survived"].astype(int)
    
    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    submission.to_csv(output_path, index=False)
    
    print(f"\n{'='*60}")
    print(f"  提交文件已生成")
    print(f"{'='*60}")
    print(f"  路径: {output_path}")
    print(f"  样本数: {len(submission)}")
    print(f"  生存率: {submission['Survived'].mean():.2%}")
    print(f"\n  提交文件预览:")
    print(submission.head())
    
    return output_path


def full_training_pipeline(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str = "Survived",
    tune: bool = False,
    create_ensemble: bool = False,
    output_dir: str = "submissions"
) -> Dict:
    """
    完整训练流程
    
    Args:
        train_df: 训练集
        test_df: 测试集
        feature_cols: 特征列
        target_col: 目标列
        tune: 是否进行超参数调优
        create_ensemble: 是否创建集成模型
        output_dir: 输出目录
        
    Returns:
        结果字典
    """
    print("\n" + "="*60)
    print("  泰坦尼克号 - 完整训练流程")
    print("="*60)
    
    # 准备数据
    available_features = [c for c in feature_cols if c in train_df.columns]
    X = train_df[available_features].copy()
    y = train_df[target_col].copy()
    
    # 处理缺失值
    X = X.fillna(0)
    test_features = test_df[available_features].copy().fillna(0)
    
    # 划分数据
    X_train, X_val, y_train, y_val = split_data(X, y)
    
    # 初始化模型
    models = get_default_models()
    
    # 评估模型
    print("\n" + "="*60)
    print("  模型评估")
    print("="*60)
    eval_results = evaluate_models(models, X_train, y_train, X_val, y_val)
    
    # 交叉验证
    print("\n" + "="*60)
    print("  交叉验证")
    print("="*60)
    cv_results = cross_validate_models(models, X, y)
    
    # 获取最佳模型
    best_model_name = eval_results.iloc[0]["Model"]
    best_model = models[best_model_name]
    
    print(f"\n【最佳模型】{best_model_name} (验证集准确率: {eval_results.iloc[0]['Val_Accuracy']:.4f})")
    
    # 超参数调优
    if tune:
        print("\n【超参数调优】")
        best_model, best_params, best_score = tune_hyperparameters(
            X, y, model_type=_get_model_type(best_model_name)
        )
        best_model_name = f"Tuned_{best_model_name}"
    
    # 集成学习
    if create_ensemble:
        print("\n【创建集成模型】")
        # 选择前3个模型
        top_models = list(models.items())[:3]
        ensemble = create_ensemble_model(dict(top_models), voting="soft")
        ensemble.fit(X, y)
        
        # 评估集成模型
        ensemble_pred = ensemble.predict(X_val)
        ensemble_acc = accuracy_score(y_val, ensemble_pred)
        print(f"  集成模型验证准确率: {ensemble_acc:.4f}")
        
        if ensemble_acc > eval_results.iloc[0]["Val_Accuracy"]:
            print("  集成模型更优，使用集成模型！")
            best_model = ensemble
            best_model_name = "Ensemble"
    
    # 在全量数据上重新训练最佳模型
    print("\n【在全量数据上重新训练最佳模型】")
    final_model = best_model.__class__(**best_model.get_params())
    final_model.fit(X, y)
    
    # 生成提交文件
    passenger_ids = test_df["PassengerId"].astype(int)
    submission_path = os.path.join(output_dir, "titanic_submission.csv")
    generate_submission(final_model, test_df, passenger_ids, available_features, submission_path)
    
    # 特征重要性
    if hasattr(final_model, "feature_importances_") or hasattr(final_model, "coef_"):
        print("\n【特征重要性 Top 10】")
        plot_feature_importance(final_model, available_features, top_n=10)
    
    return {
        "best_model": final_model,
        "best_model_name": best_model_name,
        "eval_results": eval_results,
        "cv_results": cv_results,
        "submission_path": submission_path,
        "feature_cols": available_features,
    }


def _get_model_type(model_name: str) -> str:
    """
    将模型名称映射到调优类型
    
    Args:
        model_name: 模型名称
        
    Returns:
        调优类型名
    """
    mapping = {
        "LogisticRegression": "logistic_regression",
        "RandomForest": "random_forest",
        "GradientBoosting": "gradient_boosting",
        "SVM": "svm",
        "KNN": "knn",
    }
    return mapping.get(model_name, "random_forest")