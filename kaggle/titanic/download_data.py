"""
泰坦尼克号案例 - 数据下载脚本
Titanic Case - Data Download Helper

使用 Kaggle API 下载数据集
"""

import os
import sys
import subprocess


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def check_kaggle_api():
    """检查 Kaggle API 是否已配置"""
    try:
        import kaggle
        print("✅ Kaggle API 已安装")
        return True
    except ImportError:
        print("❌ Kaggle API 未安装")
        print("   安装命令: pip install kaggle")
        return False


def download_titanic_dataset():
    """下载泰坦尼克号数据集"""
    if not check_kaggle_api():
        return False
    
    # 检查 kaggle.json 配置
    kaggle_config = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_config):
        print("❌ Kaggle API 凭证未配置")
        print("   步骤:")
        print("   1. 访问 https://www.kaggle.com/settings/account")
        print("   2. 点击 'Create New API Token' 下载 kaggle.json")
        print(f"   3. 将 kaggle.json 放到 {os.path.expanduser('~/.kaggle/')}")
        return False
    
    # 创建数据目录
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 下载数据集
    print(f"📥 正在下载泰坦尼克号数据集到 {DATA_DIR} ...")
    try:
        subprocess.run(
            ["kaggle", "competitions", "download", "-c", "titanic", "-p", DATA_DIR],
            check=True,
            shell=True,
        )
        
        # 解压
        zip_path = os.path.join(DATA_DIR, "titanic.zip")
        if os.path.exists(zip_path):
            import zipfile
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(DATA_DIR)
            os.remove(zip_path)
            print("✅ 数据集下载并解压完成！")
            
            # 列出文件
            for f in os.listdir(DATA_DIR):
                fpath = os.path.join(DATA_DIR, f)
                size = os.path.getsize(fpath)
                print(f"   {f} ({size:,} bytes)")
            
            return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 下载失败: {e}")
        return False


def create_sample_data():
    """创建示例数据（用于没有 Kaggle API 的情况）"""
    import pandas as pd
    import numpy as np
    
    print("📝 创建示例数据 ...")
    
    # 生成模拟训练数据
    np.random.seed(42)
    n_train = 891
    
    train_data = {
        "PassengerId": range(1, n_train + 1),
        "Survived": np.random.choice([0, 1], n_train, p=[0.6, 0.4]),
        "Pclass": np.random.choice([1, 2, 3], n_train, p=[0.2, 0.3, 0.5]),
        "Name": [f"Passenger_{i}" for i in range(1, n_train + 1)],
        "Sex": np.random.choice(["male", "female"], n_train, p=[0.65, 0.35]),
        "Age": np.random.normal(30, 15, n_train).clip(0.42, 80).round(1),
        "SibSp": np.random.choice([0, 1, 2, 3, 4, 5], n_train, p=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02]),
        "Parch": np.random.choice([0, 1, 2, 3, 4, 5], n_train, p=[0.7, 0.15, 0.08, 0.04, 0.02, 0.01]),
        "Ticket": [f"A{np.random.randint(1000, 9999)}" for _ in range(n_train)],
        "Fare": np.random.exponential(50, n_train).clip(0, 512).round(2),
        "Cabin": [f"C{np.random.randint(100, 999)}" if np.random.random() < 0.2 else np.nan for _ in range(n_train)],
        "Embarked": np.random.choice(["C", "Q", "S"], n_train, p=[0.2, 0.1, 0.7]),
    }
    
    # 人为增加一些相关性
    train_df = pd.DataFrame(train_data)
    
    # 性别影响生存率
    train_df.loc[(train_df["Sex"] == "female") & (np.random.random(n_train) < 0.5), "Survived"] = 1
    train_df.loc[(train_df["Sex"] == "male") & (np.random.random(n_train) < 0.7), "Survived"] = 0
    
    # 舱位影响生存率
    train_df.loc[(train_df["Pclass"] == 1) & (np.random.random(n_train) < 0.4), "Survived"] = 1
    train_df.loc[(train_df["Pclass"] == 3) & (np.random.random(n_train) < 0.6), "Survived"] = 0
    
    # 添加一些缺失值
    missing_idx = np.random.choice(n_train, int(n_train * 0.2), replace=False)
    train_df.loc[missing_idx, "Age"] = np.nan
    train_df.loc[np.random.choice(n_train, int(n_train * 0.77), replace=False), "Cabin"] = np.nan
    
    # 生成测试数据
    n_test = 418
    test_data = {
        "PassengerId": range(892, 892 + n_test),
        "Pclass": np.random.choice([1, 2, 3], n_test, p=[0.2, 0.3, 0.5]),
        "Name": [f"Passenger_{i}" for i in range(892, 892 + n_test)],
        "Sex": np.random.choice(["male", "female"], n_test, p=[0.65, 0.35]),
        "Age": np.random.normal(30, 15, n_test).clip(0.42, 80).round(1),
        "SibSp": np.random.choice([0, 1, 2, 3, 4, 5], n_test, p=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02]),
        "Parch": np.random.choice([0, 1, 2, 3, 4, 5], n_test, p=[0.7, 0.15, 0.08, 0.04, 0.02, 0.01]),
        "Ticket": [f"B{np.random.randint(1000, 9999)}" for _ in range(n_test)],
        "Fare": np.random.exponential(50, n_test).clip(0, 512).round(2),
        "Cabin": [f"D{np.random.randint(100, 999)}" if np.random.random() < 0.2 else np.nan for _ in range(n_test)],
        "Embarked": np.random.choice(["C", "Q", "S"], n_test, p=[0.2, 0.1, 0.7]),
    }
    
    test_df = pd.DataFrame(test_data)
    
    # 添加缺失值
    missing_idx_test = np.random.choice(n_test, int(n_test * 0.2), replace=False)
    test_df.loc[missing_idx_test, "Age"] = np.nan
    test_df.loc[np.random.choice(n_test, int(n_test * 0.77), replace=False), "Cabin"] = np.nan
    
    # 保存
    os.makedirs(DATA_DIR, exist_ok=True)
    train_df.to_csv(os.path.join(DATA_DIR, "train.csv"), index=False)
    test_df.to_csv(os.path.join(DATA_DIR, "test.csv"), index=False)
    
    print("✅ 示例数据已创建！")
    print(f"   训练集: {train_df.shape[0]} 行 × {train_df.shape[1]} 列")
    print(f"   测试集: {test_df.shape[0]} 行 × {test_df.shape[1]} 列")
    print(f"   位置: {DATA_DIR}")
    print(f"\n   ⚠️ 注意: 这是示例数据，实际比赛请下载真实数据集！")


if __name__ == "__main__":
    print("=" * 60)
    print("  泰坦尼克号数据下载")
    print("=" * 60)
    
    # 检查数据是否已存在
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    
    if os.path.exists(train_path) and os.path.exists(test_path):
        print(f"✅ 数据文件已存在")
        print(f"   {train_path}")
        print(f"   {test_path}")
    else:
        # 尝试通过 Kaggle API 下载
        success = download_titanic_dataset()
        
        if not success:
            # 如果失败，创建示例数据
            print("\n📌 创建示例数据以便测试流程 ...")
            create_sample_data()