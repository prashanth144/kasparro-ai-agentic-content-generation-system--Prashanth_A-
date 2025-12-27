from typing import Dict, Any, Callable

class TemplateEngine:
    def __init__(self):
        self._registry = {}

    def register_template(self, name: str, structure: Dict):
        """Register a template schema."""
        self._registry[name] = structure

    def render(self, template_name: str, context: Dict[str, Any], logic_blocks: Dict[str, Callable] = None) -> Dict:
        """
        Renders a template by filling slots from context and running logic blocks.
        """
        if template_name not in self._registry:
            raise ValueError(f"Template {template_name} not found.")
        
        template = self._registry[template_name]
        output = {}

       
        def _process_node(node):
            if isinstance(node, str):
           
                if node.startswith("{{") and node.endswith("}}"):
                    key = node[2:-2].strip()
                  
                    if key.startswith("BLOCK:"):
                        block_name = key.split(":")[1]
                        if logic_blocks and block_name in logic_blocks:
                            return logic_blocks[block_name](context)
                    return context.get(key, f"MISSING: {key}")
                return node
            elif isinstance(node, dict):
                return {k: _process_node(v) for k, v in node.items()}
            elif isinstance(node, list):
                return [_process_node(i) for i in node]
            return node

        return _process_node(template)