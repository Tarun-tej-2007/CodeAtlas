import tree_sitter
import tree_sitter_javascript as ts_js

p_js = tree_sitter.Parser(tree_sitter.Language(ts_js.language()))

code = """
import React, { useState as st } from 'react';
import * as utils from './utils';
import './styles.css';
export default App;
export { a, b as c };
export * from './components';
export const x = 1;
"""

tree = p_js.parse(code.encode('utf-8'))
for c in tree.root_node.children:
    print("PARENT:", c.type)
    for sub in c.children:
        print("  CHILD:", sub.type, "->", sub.text.decode('utf-8'))
        for subsub in sub.children:
            print("    SUBCHILD:", subsub.type, "->", subsub.text.decode('utf-8'))
            for s4 in subsub.children:
                print("      SUB4:", s4.type, "->", s4.text.decode('utf-8'))
