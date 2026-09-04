# -*- coding: utf-8 -*-
"""
记录层 (Writer)
    日志初始化 + 结果导出（Excel .xlsx + JSON）
    非会员账号下被脱敏的字段已在采集层归一为“会员可见/受限”，此处只做落盘。
"""
import json
import logging
import time

import pandas as pd

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


def setup_logging():
    """控制台 + 文件双通道日志"""
    config.ensure_data_dir()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        ],
        force=True,
    )


def save(results):
    """
    导出结果到 Excel 与 JSON
    :param results: [{'企业名称':..., '抓取状态':..., ...}, ...]
    :return: Excel 文件路径
    """
    config.ensure_data_dir()

    # 按固定列顺序补齐，缺失字段留空
    rows = [{col: r.get(col, '') for col in config.OUTPUT_COLUMNS} for r in results]
    df = pd.DataFrame(rows, columns=config.OUTPUT_COLUMNS)

    try:
        df.to_excel(config.XLSX_FILE, index=False, engine='openpyxl')
        logger.info('已导出 Excel: %s (%d 行)', config.XLSX_FILE, len(df))
    except Exception as e:  # noqa: BLE001 - 导出失败不应中断，JSON 仍会写
        logger.warning('导出 Excel 失败: %s', e)

    payload = {
        'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'count': len(results),
        'results': results,
    }
    try:
        with open(config.JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info('已导出 JSON: %s', config.JSON_FILE)
    except OSError as e:
        logger.warning('导出 JSON 失败: %s', e)

    return config.XLSX_FILE
