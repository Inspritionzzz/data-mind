"""
泰坦尼克号案例 - 主流程入口
Titanic Case - Main Pipeline

运行方式: python -m kaggle.titanic.main
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kaggle.titanic.data_loader import load_data, data_overview, explore_features, plot_distributions, plot_correlation_heatmap
from kaggle.titanic.data_cleaner import clean_all
from kaggle.titanic.feature_engineering import engineer_features
from kaggle.titanic.model import full_training_pipeline


def main():
    """
    完整的泰坦尼克号生存预测流程
    """
    print("=" * 60)
    print("  泰坦尼克号案例 - 生存预测")
    print("  Titanic Survival Prediction")
    print("=" * 60)
    
    # 数据目录
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # 检查数据文件
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print(f"\n【错误】数据文件不存在！")
        print(f"  训练集: {train_path}")
        print(f"  测试集: {test_path}")
        print(f"\n请从 Kaggle 下载数据集到 kaggle/titanic/data/ 目录:")
        print(f"  https://www.kaggle.com/c/titanic/data")
        print(f"\n或者使用以下命令下载:")
        print(f"  kaggle competitions download -c titanic -p {data_dir}")
        print(f"  unzip {data_dir}/titanic.zip -d {data_dir}")
        return
    
    # ========== Step 1: 数据加载 ==========
    print("\n" + "=" * 60)
    print("  Step 1: 数据加载与探索")
    print("=" * 60)
    
    train_df, test_df = load_data(data_dir)
    
    # 数据概览
    data_overview(train_df, "训练集概览")
    data_overview(test_df, "测试集概览")
    
    # 特征探索
    explore_features(train_df)
    
    # ========== Step 2: 数据清洗 ==========
    print("\n" + "=" * 60)
    print("  Step 2: 数据清洗")
    print("=" * 60)
    
    train_df, test_df = clean_all(train_df, test_df)
    
    # ========== Step 3: 特征工程 ==========
    print("\n" + "=" * 60)
    print("  Step 3: 特征工程")
    print("=" * 60)
    
    X_train_processed, X_test_processed, feature_cols = engineer_features(train_df, test_df)
    
    # ========== Step 4: 模型训练与评估 ==========
    print("\n" + "=" * 60)
    print("  Step 4: 模型训练与评估")
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions")
    
    results = full_training_pipeline(
        train_df=X_train_processed,
        test_df=X_test_processed,
        feature_cols=feature_cols,
        target_col="Survived",
        tune=False,  # 设置为True可进行超参数调优
        create_ensemble=True,  # 使用集成学习
        output_dir=output_dir,
    )
    
    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print("  流程完成 ✓")
    print("=" * 60)
    print(f"\n  最佳模型: {results['best_model_name']}")
    print(f"  提交文件: {results['submission_path']}")
    print(f"\n  下一步:")
    print(f"  1. 提交 {results['submission_path']} 到 Kaggle")
    print(f"  2. 查看排行榜: https://www.kaggle.com/c/titanic/leaderboard")
    print(f"\n  祝好运！🚢")


if __name__ == "__main__":
    main()