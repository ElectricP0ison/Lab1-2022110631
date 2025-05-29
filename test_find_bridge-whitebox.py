import pytest
from tkinter import Tk
from app2 import GraphApp
import tkinter as tk
from collections import defaultdict

@pytest.fixture(scope="module")
def root():
    return Tk()

@pytest.fixture
def app(root):
    app = GraphApp(root)
    root.withdraw()  # 隐藏GUI窗口
    yield app
    # 清理
    app.word1_entry.delete(0, tk.END)
    app.word2_entry.delete(0, tk.END)
    app.graph.clear()

def extract_bridge_words(result_text):
    if "are:" not in result_text:
        return set()
    bridge_str = result_text.split("are: ")[1].rstrip('! .')
    parts = bridge_str.split(', ')
    bridges = []
    for part in parts:
        if ' and ' in part:
            bridges.extend(part.split(' and '))
        else:
            bridges.append(part)
    return set(bridges)

# 测试用例1：存在多个桥接词
def test_multiple_bridge_words(app):
    app.graph['word1']['word3'] = 1
    app.graph['word3']['word2'] = 1
    app.graph['word1']['word4'] = 1
    app.graph['word4']['word2'] = 1
    app.nodes = {'word1', 'word2', 'word3', 'word4'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert extract_bridge_words(result) == {'word3', 'word4'}

# 测试用例2：存在单个桥接词
def test_single_bridge_word(app):
    app.graph['word1']['word3'] = 1
    app.graph['word3']['word2'] = 1
    app.nodes = {'word1', 'word2', 'word3'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert extract_bridge_words(result) == {'word3'}

# 测试用例3：无桥接词
def test_no_bridge_words(app):
    app.graph['word1']['word3'] = 1
    app.nodes = {'word1', 'word3'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word3')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert "No bridge words" in result

# 测试用例4：word1不在图中
def test_word1_not_in_graph(app):
    app.graph['word2']['word3'] = 1
    app.nodes = {'word2', 'word3'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert "No word1 or word2 in the graph" in result

# 测试用例5：word2不在图中
def test_word2_not_in_graph(app):
    app.graph['word1']['word3'] = 1
    app.nodes = {'word1', 'word3'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert "No word1 or word2 in the graph" in result

# 测试用例6：输入大小写混合
def test_mixed_case_input(app):
    app.graph['word1']['word3'] = 1
    app.graph['word3']['word2'] = 1
    app.nodes = {'word1', 'word2', 'word3'}
    app.word1_entry.insert(0, 'Word1')
    app.word2_entry.insert(0, 'WORD2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert extract_bridge_words(result) == {'word3'}

# 测试用例7：直接相连但无桥接词
def test_direct_connection_no_bridge(app):
    app.graph['word1']['word2'] = 1
    app.nodes = {'word1', 'word2'}
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert "No bridge words" in result

# 测试用例8：word1和word2均不在图中
def test_both_words_not_in_graph(app):
    app.word1_entry.insert(0, 'word1')
    app.word2_entry.insert(0, 'word2')
    app.find_bridge()
    result = app.bridge_result.cget("text")
    assert "No word1 or word2 in the graph" in result