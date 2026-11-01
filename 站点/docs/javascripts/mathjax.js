// https://zensical.org/docs/authoring/math/#mathjax
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
  startup: {
    ready() {
      MathJax.startup.defaultReady();
      let pending = MathJax.startup.promise;
      document$.subscribe(() => {
        pending = pending.then(() => {
          MathJax.startup.output.clearCache();
          MathJax.typesetClear();
          MathJax.texReset();
          return MathJax.typesetPromise();
        }).catch(error => console.error("MathJax:", error));
      });
      component$.subscribe(({ ref }) => {
        if (ref.classList.contains("md-annotation")) {
          pending = pending.then(() => MathJax.typesetPromise([ref]))
            .catch(error => console.error("MathJax:", error));
        }
      });
    },
  },
};
