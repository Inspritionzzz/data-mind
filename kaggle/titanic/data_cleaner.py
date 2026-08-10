"""
泰坦尼克号案例 - 数据清洗模块
Titanic Case - Data Cleaning Module

处理缺失值、异常值等数据质量问题
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional


def clean_missing_ages(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    使用多种策略处理Age缺失值
    
    策略: 使用 Sex × Pclass 分组的中位数来填充
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        处理后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 按 Sex 和 Pclass 分组计算 Age 中位数
        age_median = df.groupby(["Sex", "Pclass"])["Age"].transform("median")
        df["Age"] = df["Age"].fillna(age_median)
        
        # 若仍有缺失，用整体中位数填充
        df["Age"] = df["Age"].fillna(df["Age"].median())
    
    print(f"Age 缺失值已处理 (训练集剩余: {train_df['Age'].isna().sum()}, 测试集剩余: {test_df['Age'].isna().sum()})")
    return train_df, test_df


def clean_missing_embarked(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    处理 Embarked 缺失值
    
    策略: 使用众数填充
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        处理后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        embarked_mode = df["Embarked"].mode()[0]
        df["Embarked"] = df["Embarked"].fillna(embarked_mode)
    
    print(f"Embarked 缺失值已处理 (训练集剩余: {train_df['Embarked'].isna().sum()}, 测试集剩余: {test_df['Embarked'].isna().sum()})")
    return train_df, test_df


def clean_missing_fare(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    处理 Fare 缺失值
    
    策略: 使用 Pclass × Embarked 分组的中位数填充
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        处理后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        fare_median = df.groupby(["Pclass", "Embarked"])["Fare"].transform("median")
        df["Fare"] = df["Fare"].fillna(fare_median)
        
        # 若仍有缺失，用整体中位数
        df["Fare"] = df["Fare"].fillna(df["Fare"].median())
    
    print(f"Fare 缺失值已处理 (训练集剩余: {train_df['Fare'].isna().sum()}, 测试集剩余: {test_df['Fare'].isna().sum()})")
    return train_df, test_df


def clean_cabin(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    处理 Cabin 缺失值
    
    策略: 缺失值标记为 'Unknown'，并提取客舱等级
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        处理后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 提取客舱字母（甲板）
        df["Cabin_deck"] = df["Cabin"].apply(
            lambda x: str(x)[0] if pd.notna(x) and str(x).strip() != "" else "Unknown"
        )
        # 是否有舱位
        df["Has_Cabin"] = df["Cabin"].notna().astype(int)
    
    print(f"Cabin 缺失值已处理 (新增 Cabin_deck, Has_Cabin 特征)")
    return train_df, test_df


def clean_all(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    执行完整的数据清洗流程
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        清洗后的 (train_df, test_df)
    """
    print("\n" + "="*60)
    print("  数据清洗流程")
    print("="*60)
    
    train_df, test_df = clean_missing_ages(train_df, test_df)
    train_df, test_df = clean_missing_embarked(train_df, test_df)
    train_df, test_df = clean_missing_fare(train_df, test_df)
    train_df, test_df = clean_cabin(train_df, test_df)
    
    # 验证缺失值
    print(f"\n【清洗后缺失值统计】")
    for col in train_df.columns:
        train_missing = train_df[col].isna().sum()
        test_missing = test_df[col].isna().sum()
        if train_missing > 0 or test_missing > 0:
            print(f"  {col}: 训练集{train_missing}, 测试集{test_missing}")
    
    print("  数据清洗完成 ✓")
    return train_df, test_df