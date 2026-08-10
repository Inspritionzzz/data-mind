"""
泰坦尼克号案例 - 特征工程模块
Titanic Case - Feature Engineering Module

创建新特征、编码类别变量、特征选择等
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer


def extract_name_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    从姓名中提取特征: 称谓、姓氏
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        添加新特征后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 提取称谓 (Title)
        df["Title"] = df["Name"].str.extract(r",\s*([^\.]*)\.")
        
        # 合并稀有称谓
        title_mapping = {
            "Mr": "Mr",
            "Mrs": "Mrs",
            "Miss": "Miss",
            "Master": "Master",
            "Mme": "Mrs",
            "Mlle": "Miss",
            "Ms": "Miss",
            "Dr": "Rare",
            "Rev": "Rare",
            "Col": "Rare",
            "Major": "Rare",
            "Don": "Rare",
            "Dona": "Rare",
            "Lady": "Rare",
            "Sir": "Rare",
            "the Countess": "Rare",
            "Jonkheer": "Rare",
            "Capt": "Rare",
        }
        df["Title"] = df["Title"].map(title_mapping).fillna("Rare")
        
        # 姓氏
        df["LastName"] = df["Name"].str.extract(r"^([^,]+),")
    
    print(f"已提取姓名特征: Title, LastName")
    return train_df, test_df


def extract_ticket_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    从船票号中提取特征: 票号前缀、票价组
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        添加新特征后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 票号前缀
        df["Ticket_prefix"] = df["Ticket"].str.extract(r"^([A-Za-z])")
        df["Ticket_prefix"] = df["Ticket_prefix"].fillna("NONE")
        
        # 是否为数字票号
        df["Ticket_is_numeric"] = df["Ticket"].str.match(r"^\d+$").astype(int)
    
    print(f"已提取船票特征: Ticket_prefix, Ticket_is_numeric")
    return train_df, test_df


def create_age_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    创建年龄相关特征: 年龄分组、年龄段
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        添加新特征后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 年龄分组 (分箱)
        bins = [0, 12, 18, 25, 35, 50, 65, 100]
        labels = ["0-12", "13-18", "19-25", "26-35", "36-50", "51-65", "66+"]
        df["Age_group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)
        
        # 年龄与舱位交互
        df["Age_Pclass"] = df["Age"] * df["Pclass"]
        
        # 是否为儿童
        df["Is_Child"] = (df["Age"] < 18).astype(int)
    
    print(f"已创建年龄特征: Age_group, Age_Pclass, Is_Child")
    return train_df, test_df


def create_fare_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    创建票价相关特征: 票价分组、人均票价
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        添加新特征后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 票价分组 (分箱)
        bins = [0, 7.91, 14.45, 31, 1000]
        labels = ["Low", "Mid_Low", "Mid", "High"]
        df["Fare_group"] = pd.cut(df["Fare"], bins=bins, labels=labels, right=False)
        
        # 人均票价
        df["Fare_per_person"] = df["Fare"] / (df["SibSp"] + df["Parch"] + 1)
        
        # 对数票价
        df["Fare_log"] = np.log1p(df["Fare"])
    
    print(f"已创建票价特征: Fare_group, Fare_per_person, Fare_log")
    return train_df, test_df


def create_family_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    创建家庭相关特征: 家庭规模、单人旅行
    
    Args:
        train_df: 训练集
        test_df: 测试集
        
    Returns:
        添加新特征后的 (train_df, test_df)
    """
    for df in [train_df, test_df]:
        # 家庭规模
        df["Family_size"] = df["SibSp"] + df["Parch"] + 1
        
        # 家庭类型
        def family_type(size):
            if size == 1:
                return "Solo"
            elif size <= 4:
                return "Small"
            else:
                return "Large"
        
        df["Family_type"] = df["Family_size"].apply(family_type)
        
        # 是否单独旅行
        df["Is_Alone"] = (df["Family_size"] == 1).astype(int)
    
    print(f"已创建家庭特征: Family_size, Family_type, Is_Alone")
    return train_df, test_df


def encode_categorical_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    categorical_cols: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    对类别特征进行编码 (One-Hot Encoding)
    
    Args:
        train_df: 训练集
        test_df: 测试集
        categorical_cols: 类别特征列名列表
        
    Returns:
        编码后的 (train_df, test_df)
    """
    # 合并训练集和测试集以确保编码一致
    combined = pd.concat([train_df[categorical_cols], test_df[categorical_cols]], axis=0)
    
    encoded_dfs = []
    for col in categorical_cols:
        # 获取所有类别
        all_categories = combined[col].unique()
        
        # 创建One-Hot编码
        for category in all_categories:
            col_name = f"{col}_{category}"
            encoded_dfs.append(
                train_df[col].apply(lambda x: 1 if x == category else 0).rename(col_name)
            )
            encoded_dfs.append(
                test_df[col].apply(lambda x: 1 if x == category else 0).rename(col_name)
            )
    
    # 将编码结果添加回原数据框
    train_encoded = pd.concat(encoded_dfs[::2], axis=1)
    test_encoded = pd.concat(encoded_dfs[1::2], axis=1)
    
    train_df = pd.concat([train_df, train_encoded], axis=1)
    test_df = pd.concat([test_df, test_encoded], axis=1)
    
    # 删除原始类别列
    train_df = train_df.drop(columns=categorical_cols)
    test_df = test_df.drop(columns=categorical_cols)
    
    print(f"已对 {len(categorical_cols)} 个类别特征进行 One-Hot 编码: {categorical_cols}")
    return train_df, test_df


def encode_binary_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    binary_cols: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    对二元特征进行标签编码
    
    Args:
        train_df: 训练集
        test_df: 测试集
        binary_cols: 二元特征列名列表
        
    Returns:
        编码后的 (train_df, test_df)
    """
    le = LabelEncoder()
    
    for col in binary_cols:
        # 在合并的数据上fit
        combined = pd.concat([train_df[col], test_df[col]], axis=0)
        le.fit(combined)
        
        train_df[f"{col}_encoded"] = le.transform(train_df[col])
        test_df[f"{col}_encoded"] = le.transform(test_df[col])
    
    # 删除原始列
    train_df = train_df.drop(columns=binary_cols)
    test_df = test_df.drop(columns=binary_cols)
    
    print(f"已对 {len(binary_cols)} 个二元特征进行标签编码: {binary_cols}")
    return train_df, test_df


def select_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    drop_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    特征选择 - 移除不需要的列
    
    Args:
        train_df: 训练集
        test_df: 测试集
        drop_cols: 需要移除的列
        
    Returns:
        (X_train, X_test, selected_features)
    """
    if drop_cols is None:
        drop_cols = [
            "PassengerId", "Name", "Ticket", "Cabin",
            "LastName", "Title", "Cabin_deck", "Embarked",
            "Sex", "Age_group", "Fare_group", "Ticket_prefix",
            "Ticket", "Fare_group", "Family_type"
        ]
    
    # 只保留存在的列
    existing_drop_cols = [col for col in drop_cols if col in train_df.columns]
    
    X_train = train_df.drop(columns=existing_drop_cols, errors="ignore")
    X_test = test_df.drop(columns=existing_drop_cols, errors="ignore")
    
    # 去除重复列
    X_train = X_train.loc[:, ~X_train.columns.duplicated()]
    X_test = X_test.loc[:, ~X_test.columns.duplicated()]
    
    selected_features = list(X_train.columns)
    
    print(f"\n【特征选择】")
    print(f"  移除列: {existing_drop_cols}")
    print(f"  保留特征数: {len(selected_features)}")
    print(f"  保留特征: {selected_features}")
    
    return X_train, X_test, selected_features


def engineer_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    执行完整的特征工程流程
    
    Args:
        train_df: 已清洗的训练集
        test_df: 已清洗的测试集
        
    Returns:
        (X_train, X_test, selected_features)
    """
    print("\n" + "="*60)
    print("  特征工程流程")
    print("="*60)
    
    # 1. 提取新特征
    train_df, test_df = extract_name_features(train_df, test_df)
    train_df, test_df = extract_ticket_features(train_df, test_df)
    train_df, test_df = create_age_features(train_df, test_df)
    train_df, test_df = create_fare_features(train_df, test_df)
    train_df, test_df = create_family_features(train_df, test_df)
    
    # 2. 编码类别特征
    categorical_cols = ["Embarked", "Title", "Family_type", "Ticket_is_numeric"]
    categorical_cols = [c for c in categorical_cols if c in train_df.columns]
    if categorical_cols:
        train_df, test_df = encode_categorical_features(train_df, test_df, categorical_cols)
    
    # 3. 编码二元特征
    binary_cols = ["Sex"]
    binary_cols = [c for c in binary_cols if c in train_df.columns]
    if binary_cols:
        train_df, test_df = encode_binary_features(train_df, test_df, binary_cols)
    
    # 4. 特征选择
    # 移除非特征列 (但保留Survived用于后续分割)
    X_train = train_df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin", "LastName"], errors="ignore")
    X_test = test_df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin", "LastName"], errors="ignore")
    
    # 移除重复列
    X_train = X_train.loc[:, ~X_train.columns.duplicated()]
    X_test = X_test.loc[:, ~X_test.columns.duplicated()]
    
    # 记录所有特征列（排除目标变量）
    feature_cols = [c for c in X_train.columns if c != "Survived"]
    
    print(f"\n【最终特征集】")
    print(f"  特征数量: {len(feature_cols)}")
    print(f"  特征列表: {feature_cols}")
    
    return X_train, X_test, feature_cols