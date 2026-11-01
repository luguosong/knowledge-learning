(() => {
  const frames = new Map();
  let active = null;
  let drag = null;

  const dialog = document.createElement("dialog");
  dialog.className = "diagram-preview";
  dialog.setAttribute("aria-label", "图表预览");
  dialog.innerHTML = `
    <div class="diagram-preview__toolbar">
      <strong>图表预览</strong>
      <button type="button" data-action="out" aria-label="缩小">−</button>
      <output aria-live="polite" aria-label="缩放比例">100%</output>
      <button type="button" data-action="in" aria-label="放大">+</button>
      <button type="button" data-action="fit">复位</button>
      <button type="button" data-action="close" autofocus>关闭</button>
    </div>
    <div class="diagram-preview__stage"></div>
    <p class="diagram-preview__hint">按住左键拖拽 · 滚轮缩放 · Esc 关闭</p>
  `;
  document.body.append(dialog);
  const stage = dialog.querySelector(".diagram-preview__stage");
  const percentage = dialog.querySelector("output");

  function fitInline(frame) {
    const diagram = frames.get(frame);
    if (!diagram || diagram.parentElement !== frame) return;
    const width = diagram.offsetWidth;
    const height = diagram.offsetHeight;
    if (!width || !height) return;
    const style = getComputedStyle(frame);
    const paddingX = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
    const paddingY = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
    const borderY = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    const availableWidth = Math.max(1, frame.clientWidth - paddingX);
    const availableHeight = Math.max(1, innerHeight * 0.6 - paddingY - borderY);
    const scale = Math.min(1, availableWidth / width, availableHeight / height);
    const x = parseFloat(style.paddingLeft) + (availableWidth - width * scale) / 2;
    diagram.style.transform = `translate(${x}px, ${style.paddingTop}) scale(${scale})`;
    frame.style.height = `${height * scale + paddingY + borderY}px`;
  }

  const resize = new ResizeObserver(entries => {
    for (const { target } of entries) fitInline(target);
  });

  function prepare(root) {
    const diagrams = root.matches?.(".md-typeset div.mermaid") ? [root] : [];
    diagrams.push(...root.querySelectorAll(".md-typeset div.mermaid"));
    for (const diagram of diagrams) {
      if (diagram.closest(".diagram-frame, .diagram-preview")) continue;
      const frame = document.createElement("div");
      frame.className = "diagram-frame";
      frame.tabIndex = 0;
      frame.setAttribute("role", "button");
      frame.setAttribute("aria-label", "预览图表：双击或按 Enter 键打开");
      frame.title = "双击预览图表";
      diagram.replaceWith(frame);
      frame.append(diagram);
      frames.set(frame, diagram);
      fitInline(frame);
      resize.observe(frame);
    }
  }

  function render() {
    active.diagram.style.transform = `translate(${active.x}px, ${active.y}px) scale(${active.scale})`;
    percentage.value = `${Math.round(active.scale * 100)}%`;
  }

  function fitPreview() {
    if (!active) return;
    active.fit = Math.min(1, (stage.clientWidth - 32) / active.width, (stage.clientHeight - 32) / active.height);
    active.scale = active.fit;
    active.x = (stage.clientWidth - active.width * active.scale) / 2;
    active.y = (stage.clientHeight - active.height * active.scale) / 2;
    render();
  }

  function zoom(factor, x = stage.clientWidth / 2, y = stage.clientHeight / 2) {
    if (!active) return;
    const scale = Math.min(8, Math.max(Math.min(0.1, active.fit), active.scale * factor));
    const ratio = scale / active.scale;
    active.x = x - (x - active.x) * ratio;
    active.y = y - (y - active.y) * ratio;
    active.scale = scale;
    render();
  }

  function open(frame) {
    if (active) return;
    const diagram = frames.get(frame);
    active = { frame, diagram, width: diagram.offsetWidth, height: diagram.offsetHeight };
    // 移动原节点可保留 Zensical 的封闭 Shadow DOM、SVG 样式及事件。
    stage.append(diagram);
    dialog.showModal();
    document.body.classList.add("diagram-preview-open");
    fitPreview();
  }

  document.addEventListener("dblclick", event => {
    const frame = event.target.closest(".diagram-frame");
    if (event.button === 0 && frames.has(frame)) {
      event.preventDefault();
      open(frame);
    }
  });

  document.addEventListener("keydown", event => {
    if (event.target.matches(".diagram-frame") && ["Enter", " "].includes(event.key)) {
      event.preventDefault();
      open(event.target);
    }
  });

  dialog.addEventListener("click", event => {
    switch (event.target.closest("button")?.dataset.action) {
      case "in": zoom(1.25); break;
      case "out": zoom(0.8); break;
      case "fit": fitPreview(); break;
      case "close": dialog.close(); break;
    }
  });

  dialog.addEventListener("close", () => {
    if (!active) return;
    const { frame, diagram } = active;
    frame.append(diagram);
    active = null;
    drag = null;
    stage.classList.remove("is-dragging");
    document.body.classList.remove("diagram-preview-open");
    fitInline(frame);
    frame.focus({ preventScroll: true });
  });

  stage.addEventListener("wheel", event => {
    if (!active) return;
    event.preventDefault();
    const rect = stage.getBoundingClientRect();
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? stage.clientHeight : 1;
    const delta = Math.max(-100, Math.min(100, event.deltaY * unit));
    zoom(Math.exp(-delta * 0.002), event.clientX - rect.left, event.clientY - rect.top);
  }, { passive: false });

  stage.addEventListener("pointerdown", event => {
    if (!active || event.button !== 0) return;
    event.preventDefault();
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY };
    stage.setPointerCapture(event.pointerId);
    stage.classList.add("is-dragging");
  });

  stage.addEventListener("pointermove", event => {
    if (!active || drag?.id !== event.pointerId) return;
    active.x += event.clientX - drag.x;
    active.y += event.clientY - drag.y;
    drag.x = event.clientX;
    drag.y = event.clientY;
    render();
  });

  function endDrag(event) {
    if (drag?.id !== event.pointerId) return;
    if (stage.hasPointerCapture(event.pointerId)) stage.releasePointerCapture(event.pointerId);
    drag = null;
    stage.classList.remove("is-dragging");
  }
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);
  stage.addEventListener("lostpointercapture", endDrag);

  new MutationObserver(records => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) prepare(node);
      }
    }
    for (const frame of frames.keys()) {
      if (frame.isConnected) continue;
      resize.unobserve(frame);
      frames.delete(frame);
    }
  }).observe(document.body, { childList: true, subtree: true });

  window.addEventListener("resize", () => {
    for (const frame of frames.keys()) fitInline(frame);
    fitPreview();
  });
  prepare(document);
})();
