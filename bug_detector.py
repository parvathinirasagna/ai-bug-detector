import ast
import re
from typing import List, Dict
import astroid

class BugDetector:
    """Core bug detection engine using AST analysis"""
    
    def __init__(self):
        self.syntax_errors = []
        self.logical_bugs = []
        self.antipatterns = []
        
    def analyze_code(self, code: str, language: str = 'python') -> Dict:
        """Main analysis function"""
        self.syntax_errors = []
        self.logical_bugs = []
        self.antipatterns = []
        
        if language.lower() == 'python':
            return self._analyze_python(code)
        elif language.lower() in ['javascript', 'js']:
            return self._analyze_javascript(code)
        else:
            return self._analyze_generic(code)
    
    def _analyze_python(self, code: str) -> Dict:
        """Analyze Python code for bugs"""
        results = {
            'syntax_errors': [],
            'logical_bugs': [],
            'antipatterns': [],
            'severity': 'low'
        }
        
        # Syntax Error Detection
        try:
            ast.parse(code)
        except SyntaxError as e:
            results['syntax_errors'].append({
                'line': e.lineno,
                'message': f"Syntax Error: {e.msg}",
                'severity': 'critical'
            })
            results['severity'] = 'critical'
            return results
        
        # AST-based analysis
        try:
            tree = astroid.parse(code)
            
            # Detect logical bugs
            results['logical_bugs'].extend(self._detect_mutable_defaults(tree))
            results['logical_bugs'].extend(self._detect_division_by_zero(tree))
            results['logical_bugs'].extend(self._detect_missing_return(tree))
            
            # Detect antipatterns
            results['antipatterns'].extend(self._detect_unused_vars(tree))
            results['antipatterns'].extend(self._detect_unreachable_code(tree))
            results['antipatterns'].extend(self._detect_empty_except(tree))
            
        except Exception as e:
            results['syntax_errors'].append({
                'line': 1,
                'message': f"Analysis Error: {str(e)}",
                'severity': 'medium'
            })
        
        # Determine overall severity
        if results['syntax_errors']:
            results['severity'] = 'critical'
        elif results['logical_bugs']:
            results['severity'] = 'high'
        elif results['antipatterns']:
            results['severity'] = 'medium'
        
        return results
    
    def _detect_unused_vars(self, tree) -> List[Dict]:
        """Detect unused variables"""
        antipatterns = []
        defined_vars = set()
        used_vars = set()
        
        for node in tree.nodes_of_class(astroid.AssignName):
            if not node.name.startswith('_'):
                defined_vars.add((node.name, node.lineno))
        
        for node in tree.nodes_of_class(astroid.Name):
            used_vars.add(node.name)
        
        for var_name, line in defined_vars:
            if var_name not in used_vars:
                antipatterns.append({
                    'line': line,
                    'message': f"Unused variable: '{var_name}'",
                    'severity': 'low'
                })
        
        return antipatterns
    
    def _detect_mutable_defaults(self, tree) -> List[Dict]:
        """Detect mutable default arguments"""
        bugs = []
        for node in tree.nodes_of_class(astroid.FunctionDef):
            if node.args.defaults:
                for default in node.args.defaults:
                    if isinstance(default, (astroid.List, astroid.Dict)):
                        bugs.append({
                            'line': node.lineno,
                            'message': f"Mutable default argument in '{node.name}' - can cause bugs",
                            'severity': 'high'
                        })
        return bugs
    
    def _detect_division_by_zero(self, tree) -> List[Dict]:
        """Detect potential division by zero"""
        bugs = []
        for node in tree.nodes_of_class(astroid.BinOp):
            if node.op in ['/', '//', '%']:
                if isinstance(node.right, astroid.Const) and node.right.value == 0:
                    bugs.append({
                        'line': node.lineno,
                        'message': "Division by zero detected",
                        'severity': 'critical'
                    })
        return bugs
    
    def _detect_unreachable_code(self, tree) -> List[Dict]:
        """Detect unreachable code after return"""
        antipatterns = []
        for node in tree.nodes_of_class(astroid.FunctionDef):
            try:
                for stmt_idx, stmt in enumerate(node.body):
                    if isinstance(stmt, astroid.Return):
                        if stmt_idx < len(node.body) - 1:
                            antipatterns.append({
                                'line': node.body[stmt_idx + 1].lineno,
                                'message': "Unreachable code after return",
                                'severity': 'medium'
                            })
                            break
            except:
                pass
        return antipatterns
    
    def _detect_empty_except(self, tree) -> List[Dict]:
        """Detect empty except blocks"""
        antipatterns = []
        for node in tree.nodes_of_class(astroid.TryExcept):
            for handler in node.handlers:
                if not handler.body or (len(handler.body) == 1 and isinstance(handler.body[0], astroid.Pass)):
                    antipatterns.append({
                        'line': handler.lineno,
                        'message': "Empty except block - exceptions silently ignored",
                        'severity': 'medium'
                    })
        return antipatterns
    
    def _detect_missing_return(self, tree) -> List[Dict]:
        """Detect functions with inconsistent returns"""
        bugs = []
        for node in tree.nodes_of_class(astroid.FunctionDef):
            if node.name.startswith('_'):
                continue
            
            has_return = False
            has_return_value = False
            
            for child in node.nodes_of_class(astroid.Return):
                has_return = True
                if child.value is not None:
                    has_return_value = True
            
            if has_return and not has_return_value and len(node.body) > 1:
                bugs.append({
                    'line': node.lineno,
                    'message': f"Function '{node.name}' has return without value",
                    'severity': 'medium'
                })
        
        return bugs
    
    def _analyze_javascript(self, code: str) -> Dict:
        """Basic JavaScript analysis"""
        results = {
            'syntax_errors': [],
            'logical_bugs': [],
            'antipatterns': [],
            'severity': 'low'
        }
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if '==' in line and '===' not in line:
                results['antipatterns'].append({
                    'line': i,
                    'message': "Use '===' instead of '=='",
                    'severity': 'low'
                })
            
            if re.search(r'\bvar\b', line):
                results['antipatterns'].append({
                    'line': i,
                    'message': "Use 'let' or 'const' instead of 'var'",
                    'severity': 'low'
                })
        
        if results['antipatterns']:
            results['severity'] = 'medium'
        
        return results
    
    def _analyze_generic(self, code: str) -> Dict:
        """Generic code analysis"""
        results = {
            'syntax_errors': [],
            'logical_bugs': [],
            'antipatterns': [],
            'severity': 'low'
        }
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line:
                results['antipatterns'].append({
                    'line': i,
                    'message': "Unresolved TODO/FIXME comment",
                    'severity': 'low'
                })
        
        return results
