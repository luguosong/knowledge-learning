# JVM

JVM 知识合并两条主线：系统学习路线，与 Oracle 教程「跨平台 + 运行时优化」原文的解释。


本节合并两条记录：JVM 的系统学习路线，以及 Oracle 教程中「跨平台 + 运行时优化」原文的解释。

## 跨平台与 HotSpot 运行时优化

**结论**：Oracle 教程那段话讲两层机制。跨平台：javac 把源码编译为平台无关的字节码（bytecode），各操作系统各自移植 Java 虚拟机（Java Virtual Machine，JVM），把同一份字节码翻译为本机代码；前提是目标系统装有对应 JVM，代价是比直接执行本机代码多一层翻译。

```text
Hello.java
    >
[javac 编译]
    >
Hello.class（平台无关字节码）
    >
    +----------------+----------------+
    |                |                |
 Windows JVM     Linux JVM        Mac JVM
    >                >                >
 本机代码          本机代码         本机代码
```

HotSpot 运行时优化：「查找性能瓶颈」即运行时性能分析（profiling），「重新编译为本机代码」即 JIT。不在编译期全部编译为本机码，是为了保住跨平台，并利用只有运行时才有的信息（热点、类型分布）。HotSpot 用分层编译：C1 快速编译并采集信息，C2 据此深度优化。教程以「一些虚拟机」限定，因为 JIT 属实现行为，JVM 规范将指令优化留给实现。

```text
字节码 > 解释执行 > 热点探测（profiling）
                      |
                C1 快速编译 + 采集信息
                      |
                C2 深度优化（JIT）
```

## 规范与实现的边界

类文件、运行时语义和内存模型由规范定义；内存物理布局、GC 算法及 JIT 优化属于具体实现。前置：会用 Java SE 编写多线程程序，理解进程、线程、虚拟内存、CPU 缓存和基本数据结构。实验以 JDK 21 为主，规范查对应版本；Java SE 27 规范用于核对最新术语，跨版本比较时核查行为和参数。

学习路线（面向 Java 服务端开发）：

| 阶段 | 为什么先学这一层 | 最小实验与通过标准 |
| --- | --- | --- |
| 1．字节码与类文件 | 建立「源码如何成为可执行输入」的模型 | 用 `javac`、`javap -c -v` 对照循环、异常、Lambda、`synchronized`；说明常量池、栈帧和调用指令的作用 |
| 2．类加载与运行时 | 弄清类何时可用、对象和方法在哪里运行 | 写两个类加载器加载同名类；解释类身份、初始化顺序与失败 |
| 3．内存与 GC | 先识别「谁还活着」，再研究回收器 | 制造对象滞留和小堆压力；区分分配过快、存活对象过多与非堆内存增长 |
| 4．编译与并发 | 理解执行速度与可见性为何变化 | 用 JFR 观察热点、分配和锁；用并发小程序证明 happens-before；解释预热、内联、反优化、平台线程和虚拟线程 |
| 5．诊断与调优 | 把模型用于实际服务，而非记参数 | 对 CPU 高、延迟升高、内存增长、线程阻塞各做一次复现实验，保留完整证据链 |
| 6．实现专项（选学） | 按工作问题深入某个实现机制 | 选 GC、编译器、类加载/Agent 或 Native 接口；读 OpenJDK 源码并用实验说明适用 JDK 与实现 |

核心知识主题：JDK/JRE/JVM/规范与 HotSpot 的关系；类文件结构与校验；指令集与五种调用指令；类生命周期（加载→验证/准备/解析→初始化）；运行时数据区（pc、栈、堆、方法区）与各类 `OutOfMemoryError` 的区别；对象可达性与四种引用；GC 算法与 Serial、Parallel、G1、ZGC 的取舍；解释执行、分层编译与代码缓存；JMM（happens-before、数据竞争）与 `synchronized`/`volatile`/`final`/`VarHandle`；Java 堆、直接内存、线程栈与本机内存的系统边界；`-Xlog`、`jcmd`、JFR、线程/堆转储等观测手段。

## 关键边界

- JVM 规范的「方法区」是逻辑区域；HotSpot 元空间是实现中的类元数据存储，两者不能直接等同。JMM 约束多线程可观察行为，不是「堆和栈的分区图」。
- JVMS 第 5 章将 `static` 字段的默认值赋予准备阶段，将 `ConstantValue` 赋值与 `<clinit>` 放在初始化阶段；不要把口诀当成规范。
- GC 与诊断参数要按 JDK 版本核对；例如 JDK 21 的分代 ZGC 参数不能直接照搬到 JDK 25（版本差异见 [JDK：版本演化与类库体系](java-se/jdk.md)）。

最小综合练习：在测试环境给同一个小型 Java 服务制造对象滞留、频繁分配、锁竞争及大量类加载四种现象；每次只改变一个条件；采集 GC 日志、JFR 与相应转储；写出「现象 → 证据 → 原因 → 调整 → 复测」，并记录 JDK、GC、堆参数、负载和测量窗口。只有当复测显示目标指标改善，才把调整视为有效。

信源：

- [Oracle Java Tutorials：About the Java Technology（一手，所引原文出处）](https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html)
- [JDK 21：HotSpot 性能增强（一手）](https://docs.oracle.com/en/java/javase/21/vm/java-hotspot-virtual-machine-performance-enhancements.html)
- [Java SE 27 JVM 规范（一手）](https://docs.oracle.com/javase/specs/jvms/se27/html/index.html)
- [Java SE 27 语言规范：线程与锁（一手）](https://docs.oracle.com/javase/specs/jls/se27/html/jls-17.html)
- [JDK 21 HotSpot GC 指南（一手）](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [JDK 21 虚拟机指南（一手）](https://docs.oracle.com/en/java/javase/21/vm/)
- [JDK 21 诊断工具（一手）](https://docs.oracle.com/en/java/javase/21/troubleshoot/diagnostic-tools.html)

