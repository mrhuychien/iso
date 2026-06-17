export function el(tag, attrs = {}, html = "") {
  const node = document.createElement(tag);
  for (const k in attrs) {
    if (k === "class") node.className = attrs[k];
    else node.setAttribute(k, attrs[k]);
  }
  if (html) node.innerHTML = html;
  return node;
}

export function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
