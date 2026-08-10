"""
泰坦尼克号案例 - 数据加载与探索模块
Titanic Case - Data Loading & Exploration Module
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_data(data_dir: str = DATA_DIR) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    加载泰坦尼克号训练集和测试集
    
    Args:
        data_dir: 数据文件所在目录
        
    Returns:
        (train_df, test_df) 训练集和测试集DataFrame
    """
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    
    if not os.path.exists(train_path):
        raise FileNotFoundError(
            f"训练数据文件不存在: {train_path}\n"
            f"请从 Kaggle 下载数据集: https://www.kaggle.com/c/titanic/data"
        )
    if not os.path.exists(test_path):
        raise FileNotFoundError(
            f"测试数据文件不存在: {test_path}\n"
            f"请从 Kaggle 下载数据集: https://www.kaggle.com/c/titanic/data"
        )
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    print(f"训练集形状: {train_df.shape}")
    print(f"测试集形状: {test_df.shape}")
    
    return train_df, test_df


def data_overview(df: pd.DataFrame, title: str = "数据集概览") -> None:
    """
    打印数据集基本信息
    
    Args:
        df: 输入DataFrame
        title: 标题
    """
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"\n【数据形状】{df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"\n【数据类型】")
    print(df.dtypes)
    print(f"\n【缺失值统计】")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({"缺失数": missing, "缺失率%": missing_pct})
    print(missing_df[missing_df["缺失数"] > 0])
    print(f"\n【数值列统计】")
    print(df.describe())
    print(f"\n【前5行数据】")
    print(df.head())


def explore_features(train_df: pd.DataFrame) -> None:
    """
    探索各特征与生存目标的关系
    
    Args:
        train_df: 训练集DataFrame
    """
    print(f"\n{'='*60}")
    print(f"  特征探索 - 各变量与生存的关系")
    print(f"{'='*60}")
    
    # 总体生存率
    survival_rate = train_df["Survived"].mean()
    print(f"\n【总体生存率】{survival_rate:.2%}")
    
    # 按性别
    print(f"\n【性别 × 生存率】")
    sex_surv = train_df.groupby("Sex")["Survived"].agg(["sum", "count", "mean"])
    sex_surv.columns = ["存活数", "总数", "生存率"]
    print(sex_surv)
    
    # 按舱位等级
    print(f"\n【舱位等级 × 生存率】")
    pclass_surv = train_df.groupby("Pclass")["Survived"].agg(["sum", "count", "mean"])
    pclass_surv.columns = ["存活数", "总数", "生存率"]
    print(pclass_surv)
    
    # 按登船港口
    print(f"\n【登船港口 × 生存率】")
    embarked_surv = train_df.groupby("Embarked")["Survived"].agg(["sum", "count", "mean"])
    embarked_surv.columns = ["存活数", "总数", "生存率"]
    print(embarked_surv)
    
    # 年龄分布
    print(f"\n【年龄分布】")
    print(f"  有年龄记录: {train_df['Age'].notna().sum()} 人")
    print(f"  年龄缺失: {train_df['Age'].isna().sum()} 人")
    print(f"  年龄范围: {train_df['Age'].min():.1f} - {train_df['Age'].max():.1f}")
    print(f"  平均年龄: {train_df['Age'].mean():.1f}")
    
    # 票价分布
    print(f"\n【票价分布】")
    print(f"  票价范围: {train_df['Fare'].min():.2f} - {train_df['Fare'].max():.2f}")
    print(f"  平均票价: {train_df['Fare'].mean():.2f}")
    
    # 舱位数
    print(f"\n【舱位信息】")
    print(f"  有舱位记录: {train_df['Cabin'].notna().sum()} 人")
    print(f"  舱位缺失: {train_df['Cabin'].isna().sum()} 人 ({train_df['Cabin'].isna().mean():.1%})")


def plot_distributions(train_df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """
    绘制数据分布图
    
    Args:
        train_df: 训练集DataFrame
        save_path: 保存图片路径（可选）
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 生存分布
    axes[0, 0].hist(train_df["Survived"], bins=2, edgecolor="black")
    axes[0, 0].set_title("Survived Distribution")
    axes[0, 0].set_xlabel("Survived")
    axes[0, 0].set_ylabel("Count")
    
    # 性别分布
    male_surv = train_df[train_df["Sex"] == "male"]["Survived"].mean()
    female_surv = train_df[train_df["Sex"] == "female"]["Survived"].mean()
    axes[0, 1].bar(["Male", "Female"], [male_surv, female_surv], color=["blue", "pink"])
    axes[0, 1].set_title("Survival Rate by Sex")
    axes[0, 1].set_ylabel("Survival Rate")
    axes[0, 1].set_ylim(0, 1)
    
    # 舱位分布
    pclass_groups = train_df.groupby("Pclass")["Survived"].mean()
    axes[0, 2].bar(pclass_groups.index.astype(str), pclass_groups.values, color=["#d62728", "#2ca02c", "#1f77b4"])
    axes[0, 2].set_title("Survival Rate by Pclass")
    axes[0, 2].set_xlabel("Pclass")
    axes[0, 2].set_ylabel("Survival Rate")
    axes[0, 2].set_ylim(0, 1)
    
    # 年龄分布
    age_survived = train_df[train_df["Survived"] == 1]["Age"].dropna()
    age_not_survived = train_df[train_df["Survived"] == 0]["Age"].dropna()
    axes[1, 0].hist(age_survived, bins=30, alpha=0.7, label="Survived", color="green")
    axes[1, 0].hist(age_not_survived, bins=30, alpha=0.7, label="Not Survived", color="red")
    axes[1, 0].set_title("Age Distribution by Survival")
    axes[1, 0].set_xlabel("Age")
    axes[1, 0].legend()
    
    # 票价分布
    axes[1, 1].hist(train_df["Fare"].dropna(), bins=50, edgecolor="black", color="orange")
    axes[1, 1].set_title("Fare Distribution")
    axes[1, 1].set_xlabel("Fare")
    
    # 登船港口分布
    embarked_counts = train_df["Embarked"].value_counts()
    axes[1, 2].pie(embarked_counts.values, labels=embarked_counts.index, autopct="%1.1f%%")
    axes[1, 2].set_title("Embarked Distribution")
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"图表已保存: {save_path}")
    
    plt.show()


def plot_correlation_heatmap(train_df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """
    绘制相关性热力图
    
    Args:
        train_df: 训练集DataFrame
        save_path: 保存图片路径（可选）
    """
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns
    corr_matrix = train_df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="RdBu_r", center=0,
                square=True, fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap - Numeric Features")
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"热力图已保存: {save_path}")
    
    plt.show()


def get_feature_groups() -> dict:
    """
    获取特征分组信息
    
    Returns:
        特征分组字典
    """
    return {
        "target": ["Survived"],
        "passenger_info": ["PassengerId", "Name", "Age", "Sex"],
        "ticket_info": ["Ticket", "Fare", "Cabin"],
        "travel_info": ["Pclass", "SibSp", "Parch", "Embarked"],
    }