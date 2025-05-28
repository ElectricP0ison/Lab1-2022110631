import pytest
import tkinter as tk
from app2 import GraphApp
import random
random.seed(42)

root = tk.Tk()

@pytest.fixture
def app():
    app = GraphApp(root)
    yield app

def test_insert_bridge_word(app):
    # 构建图结构：a -> c -> b
    app.graph = {'a': {'c': 1}, 'c': {'b': 1}, 'b': {}}
    # 模拟输入
    app.newtext_entry.insert(0, "a b")
    app.process_text()
    assert app.newtext_result.cget("text") == "a c b"

def test_no_bridge_word(app):
    # 构建图结构：a -> c，b 不存在路径
    app.graph = {'a': {'c': 1}, 'c': {}}
    app.newtext_entry.insert(0, "a b")
    app.process_text()
    assert app.newtext_result.cget("text") == "a b"

def test_single_word_input(app):
    app.newtext_entry.insert(0, "alone")
    app.process_text()
    assert app.newtext_result.cget("text") == "alone"

def test_empty_input(app):
    app.newtext_entry.insert(0, "")
    app.process_text()
    assert app.newtext_result.cget("text") == ""

def test_multiple_bridge_selection(app, monkeypatch):
    # 构建图结构：a 有两条桥接路径到 b
    app.graph = {'a': {'c': 1, 'd': 1}, 'c': {'b': 1}, 'd': {'b': 1}, 'b': {}}
    # 固定随机选择第一个桥接词
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    app.newtext_entry.insert(0, "a b")
    app.process_text()
    assert app.newtext_result.cget("text") in ["a c b", "a d b"]

def test_case_insensitive_lookup(app):
    # 图使用小写存储
    app.graph = {'a': {'c': 1}, 'c': {'b': 1}}
    # 输入包含大写
    app.newtext_entry.insert(0, "A B")
    app.process_text()
    assert app.newtext_result.cget("text") == "A c B"

def test_punctuation_handling(app):
    app.graph = {'hello': {'world': 1}}  # 无桥接词
    app.newtext_entry.insert(0, "Hello, world!")
    app.process_text()
    # 标点被过滤，原样输出（无桥接词）
    assert app.newtext_result.cget("text") == "Hello world"

def test_multiple_pairs_processing(app):
    # 构建多对桥接词
    app.graph = {
        'a': {'b': 1},  # 无桥接需要
        'b': {'c': 1}, 
        'c': {'d': 1},
        'd': {'e': 1}
    }
    app.newtext_entry.insert(0, "a b c d")
    app.process_text()
    # 预期所有词对都被处理，但只有存在桥接词时才会插入
    # 此例中假设没有桥接词，所以输出原样
    assert app.newtext_result.cget("text") == "a b c d"

def test_realistic_scenario(app, monkeypatch):
    # 完整场景测试
    app.graph = {
        'project': {'management': 3, 'planning': 2},
        'management': {'software': 1},
        'planning': {'phase': 2},
        'phase': {'software': 4},
        'software': {}
    }
    # 固定随机选择第一个桥接词
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    app.newtext_entry.insert(0, "Project planning phase")
    app.process_text()
    # 预期输出可能为 "Project management planning phase software"
    # 根据实际桥接词存在情况调整断言
    assert "management" in app.newtext_result.cget("text").split()

def test_consecutive_bridge_insertion(graph, monkeypatch):
    """测试连续桥接词插入"""
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    graph.graph = {
        'start': {'mid': 3},
        'mid': {'end': 5},
        'end': {}
    }
    graph._build_full_index()
    input_text = "start end"
    result = graph.generate_new_text(input_text)
    assert result == "Start mid end"

def test_cascading_bridges(graph, monkeypatch):
    """测试级联桥接词场景"""
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    graph.graph = {
        'a': {'b1': 1, 'b2': 1},
        'b1': {'c': 1},
        'b2': {'c': 1},
        'c': {'d': 1},
        'd': {}
    }
    graph._build_full_index()
    input_text = "a d"
    result = graph.generate_new_text(input_text)
    # 期望路径：a -> b1 -> c -> d 或 a -> b2 -> c -> d
    assert result.count(" ") == 3  # 原始2词 + 2桥接词

def test_duplicate_edges(graph, monkeypatch):
    """测试重复边权重处理"""
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    graph.graph = {
        'from': {'bridge1': 3, 'bridge2': 3},
        'bridge1': {'to': 2},
        'bridge2': {'to': 2},
        'to': {}
    }
    graph._build_full_index()
    input_text = "from to"
    result = graph.generate_new_text(input_text)
    assert result in ["From bridge1 to", "From bridge2 to"]

def test_stopword_processing(graph):
    """测试停用词处理（假设包含停用词过滤）"""
    graph.graph = {
        'analyzing': {'data': 1},
        'data': {'patterns': 1},
        'patterns': {}
    }
    graph._build_full_index()
    input_text = "analyzing the data patterns"
    result = graph.generate_new_text(input_text)
    # 假设"the"被过滤后变成 analyzing data patterns
    assert result == "Analyzing data patterns"

def test_numeric_handling(graph, monkeypatch):
    """测试数字单词处理"""
    monkeypatch.setattr(random, 'choice', lambda x: x[0])
    graph.graph = {
        'version': {'2': 1},
        '2': {'release': 1},
        'release': {}
    }
    graph._build_full_index()
    input_text = "version 2 release"
    result = graph.generate_new_text(input_text)
    assert result == "Version 2 release"
