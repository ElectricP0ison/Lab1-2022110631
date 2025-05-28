import pytest
import random
from tkinter import Tk
from unittest.mock import patch
from app2 import GraphApp  # 替换为实际模块名
random.seed(42)

root = Tk()

@pytest.fixture(scope="function")
def app():
    app = GraphApp(root)
    app.graph.clear()
    app.nodes = []
    yield app

def test_no_bridge_word(app):
    # 构造图结构：a 和 c 无桥接词
    app.graph['a']['x'] = 1
    app.graph['c']['y'] = 1
    app.nodes = ['a', 'x', 'c', 'y']
    app.newtext_entry.insert(0, "a c")
    app.process_text()
    assert app.newtext_result.cget("text") == "a c"

def test_single_bridge_word(app):
    # 构造图结构：a -> b -> c
    app.graph['a']['b'] = 1
    app.graph['b']['c'] = 1
    app.nodes = ['a', 'b', 'c']
    with patch('random.choice', return_value='b'):
        app.newtext_entry.insert(0, "a c")
        app.process_text()
        assert app.newtext_result.cget("text") == "a b c"

def test_multiple_bridge_words(app):
    # 构造图结构：a 可通过 b1 或 b2 到达 c
    app.graph['a']['b1'] = 1
    app.graph['b1']['c'] = 1
    app.graph['a']['b2'] = 1
    app.graph['b2']['c'] = 1
    app.nodes = ['a', 'b1', 'b2', 'c']
    with patch('random.choice', return_value='b1'):
        app.newtext_entry.insert(0, "a c")
        app.process_text()
        assert app.newtext_result.cget("text") == "a b1 c"

def test_punctuation_handling(app):
    # 验证标点被正确忽略
    app.graph['a']['b'] = 1
    app.graph['b']['c'] = 1
    app.nodes = ['a', 'b', 'c']
    with patch('random.choice', return_value='b'):
        app.newtext_entry.insert(0, "a, c!")
        app.process_text()
        assert app.newtext_result.cget("text") == "a b c"

def test_case_insensitive(app):
    # 验证输入大写被当作小写处理
    app.graph['a']['b'] = 1
    app.graph['b']['c'] = 1
    app.nodes = ['a', 'b', 'c']
    with patch('random.choice', return_value='b'):
        app.newtext_entry.insert(0, "A C")
        app.process_text()
        assert app.newtext_result.cget("text") == "a b c"