# Java

Java 领域围绕服务端 Java 展开：专家学习路线、日志体系、虚拟机机制与企业平台规范。主线是先形成可测试的服务，再以故障诊断与设计取舍深化专项；知识清单不等于已经掌握。

## Java 专家的学习路线：18 个领域与专项

**结论**：建议覆盖 18 个主干领域，并在运行时与性能、框架与基础设施、分布式系统或安全等方向中选一个专项深入。验收按「会实现 → 能解释原理 → 能诊断故障 → 能论证取舍」递进。领域划分、顺序和验收要求是基于一手资料的学习建议，不是官方统一认证标准。

### 主线与阶段标记

标记含义：A＝先掌握，B＝完成单体服务后深入，C＝按专项选学。A 与 B 是阶段，不代表能力上限。练习可以沿用 JDK 21，再用 JDK 25 对照版本差异；语言特性、API、预览状态和框架兼容性以对应版本文档为准。

```text
+ Java SE、算法与工程基础
|
+ 网络、数据库与 Spring 单体服务
|
+ 并发、JVM 与性能诊断
|
+ 缓存、消息与分布式系统
|
+ 选择专项 > 解决复杂问题 > 沉淀成果

测试 - 安全 - 文档 - 源码阅读：贯穿以上全部阶段
```

Java 标准版（Java Platform, Standard Edition，Java SE）的细化路线是独立专题，本节只展开总路线。

### 18 个领域与验收目标

基础与运行机制（1—5）：

| 领域 | 阶段 | 核心知识点 | 验收目标 |
| --- | --- | --- | --- |
| 1．Java SE | A，机制向 B 深入 | 语言与标准库（集合、反射、注解等） | 见独立专题 |
| 2．数据结构与算法 | A → B | 复杂度、摊还分析；数组到图等结构；二分、排序、动态规划；红黑树、B+ 树、跳表、布隆过滤器 | 按数据规模、访问方式和内存预算选结构；解释集合与数据库索引的设计 |
| 3．操作系统与硬件基础 | A → B | 进程线程与调度；用户态与内核态；虚拟内存、页缓存；CPU 缓存、缓存行与伪共享 | 区分计算、内存、磁盘与网络瓶颈；解释线程增加后性能可能下降的原因 |
| 4．并发编程 | A 基础，B 深入 | 线程状态与取消；synchronized、volatile、Lock；Java 内存模型（Java Memory Model，JMM）、happens-before；比较并交换（Compare-and-Set，CAS）与原子类；线程池、CompletableFuture、ConcurrentHashMap；虚拟线程；抽象队列同步器（AbstractQueuedSynchronizer，AQS）源码 | 实现有界并发任务；证明共享状态的正确性；模拟超时、取消、拒绝和死锁并定位原因 |
| 5．Java 虚拟机 | B | 规范与实现的区别；类加载；内存区域；垃圾回收（Garbage Collection，GC）；G1、ZGC；即时编译（Just-In-Time Compilation，JIT）与逃逸分析；内存泄漏 | 从线程转储、堆转储、GC 日志和性能记录分析内存不足、锁竞争与延迟；明确结论适用的 JDK 与实现 |

服务端工程主干（6—11）：

| 领域 | 阶段 | 核心知识点 | 验收目标 |
| --- | --- | --- | --- |
| 6．开发工具与构建 | A | IDE 调试；Git；Maven 生命周期、依赖传递、BOM、多模块 | 新环境能构建、测试并运行项目；定位一次依赖冲突 |
| 7．网络与 Web | A → B | TCP/IP、HTTP 语义、TLS、Cookie/Session、同源策略；Servlet 生命周期；远程过程调用（Remote Procedure Call，RPC）按需 | 说明一次请求从客户端到数据库再返回的完整路径；用抓包和日志定位超时 |
| 8．关系数据库 | A → B | 建模与范式；索引与执行计划；ACID、隔离级别、多版本并发控制（MVCC）、锁；预写日志（Write-Ahead Logging，WAL）、复制与迁移 | 解释并修复慢查询与并发写冲突；不将某个数据库的实现泛化到所有数据库 |
| 9．Java 数据访问 | A → B | Java 数据库连接（Java Database Connectivity，JDBC）、连接池、事务；MyBatis 或 Jakarta Persistence/Hibernate；N+1 查询、乐观锁 | 从业务方法追到实际 SQL、连接和事务；解释框架隐藏了什么、哪些问题仍由应用负责 |
| 10．Spring 体系 | A → B | 控制反转（Inversion of Control，IoC）与依赖注入；Bean 生命周期；面向切面编程（AOP）与代理；Spring MVC；事务传播与代理边界；Spring Boot 自动配置、Starter、Actuator；Spring Security | 完成可测试的单体服务；解释自动配置生效原因、调用链及事务未生效的原因 |
| 11．软件设计与架构 | A 持续，B 深入 | 内聚耦合与依赖方向；设计模式；分层与模块化单体；领域驱动设计（Domain-Driven Design，DDD）；架构决策记录（Architecture Decision Record，ADR） | 对真实需求给出简单设计；说明边界、约束、替代方案与成本 |

生产系统能力（12—18）：

| 领域 | 阶段 | 核心知识点 | 验收目标 |
| --- | --- | --- | --- |
| 12．缓存 | B | Redis；键设计与淘汰；穿透、击穿、雪崩；一致性与失效策略；分布式锁的租约 | 解释什么能缓存、允许多久不一致、失效后系统如何承受流量 |
| 13．消息与事件 | B | 队列与发布订阅；确认、重试、死信、积压；分区与顺序；至少一次语义与幂等；Outbox | 验证重复投递、消费失败、重启与乱序；说明业务结果能保证到哪一层 |
| 14．分布式系统 | B → C | 部分失败；超时、重试、退避与抖动；一致性模型与 CAP 取舍；Raft；限流、熔断、降级；Saga、Outbox；微服务边界 | 用故障实验说明网络超时、节点重启和重复请求的结果；有明确收益时才拆分服务 |
| 15．测试与质量 | A 起贯穿 | 单元到端到端测试；JUnit、参数化、测试替身；Testcontainers；属性测试；覆盖率的局限 | 测试能发现真实业务错误且结果稳定；关键事务和失败路径可重复验证 |
| 16．可观测性与性能 | A 基础，B 深入 | 结构化日志、指标、链路追踪；OpenTelemetry；延迟分位数与错误率；JDK Flight Recorder（JFR）、火焰图；JMH 微基准的预热与死代码消除 | 建立负载与性能基线；形成「现象—证据—原因—修改—复测」的诊断报告 |
| 17．应用安全 | A 起贯穿，C 可专精 | 认证授权与会话边界；OAuth 2.0、JWT 校验；注入与跨站类漏洞；反序列化与上传安全；密码存储、密钥管理、TLS | 用失败用例验证越权、非法输入与令牌校验；审查密钥和敏感信息的生命周期 |
| 18．部署与交付 | A 单机，B 容器与集群 | Linux 排查；健康检查、优雅停机；持续集成／持续交付（CI/CD）；镜像与容器资源限制；Kubernetes 的 Pod、Deployment、探针、扩缩容；滚动发布与回滚 | 在干净环境交付服务；验证重启、资源不足、发布和回滚；说明应用与平台各自负责什么 |

### 专项方向（C）：选一个深入，不要求全部精通

| 方向 | 深入内容与成果 |
| --- | --- |
| JVM 与性能 | 编译与 GC、内存与并发、操作系统与硬件；定位跨层瓶颈；形成带条件与数据的诊断、优化报告 |
| 框架与基础设施 | Spring 扩展点、注解处理、字节码增强、Java Agent；实现并维护可复用组件 |
| 分布式与数据系统 | 共识、存储、复制、恢复、调度、容量与可用性；实现故障注入实验并解释正确性边界 |
| 安全与业务领域 | Java 密码 API、证书信任、密钥生命周期、签名验证与审计；结合国密、电子签章、PKI 工作深入 |
| 启动与部署优化 | 提前编译（Ahead-of-Time Compilation，AOT）、GraalVM Native Image、启动与内存预算；比较兼容性和运维成本 |

边界：搜索引擎、文档数据库、批处理、任务调度、工作流、大数据、桌面 JavaFX、Android 属于按产品需求追加的分支，不作为主干完成标准；进入分支后另查对应官方资料。

### 阶段验收与学习方法

| 阶段 | 学习重点 | 可验证产出 |
| --- | --- | --- |
| 第一阶段 | Java SE、基本算法、Git、Maven、JUnit | 不依赖 Spring 的命令行文件处理工具，含正常、异常与边界测试 |
| 第二阶段 | HTTP、数据库、数据访问、Spring、基础安全 | 模块化单体服务，含权限、事务、迁移、错误处理和集成测试 |
| 第三阶段 | 并发、JVM、操作系统、可观测性 | 测试环境制造内存泄漏、锁竞争和线程池耗尽，保存证据并修复 |
| 第四阶段 | 缓存、消息、分布式、部署 | 为明确需求引入缓存或消息；验证重复、丢连接、重启、积压与回滚 |
| 第五阶段 | 一个专家专项、源码与规范 | 完成可复现的深入分析、组件改进或开源贡献，接受他人审查 |

每个知识点按五步学习：明确要解决的问题 → 编写最小实验 → 查 API、规范和实现 → 注入边界或故障 → 写明适用条件与取舍。源码沿问题阅读（如 HashMap 扩容、ThreadPoolExecutor 拒绝策略、Spring Bean 创建与事务代理），不从仓库第一行通读。架构、测试、安全和文档从第一阶段开始，不等后期补做。

信源：

- [Dev.java 学习目录（一手）](https://dev.java/learn/)
- [Java 语言与虚拟机规范（一手）](https://docs.oracle.com/javase/specs/)
- [JDK 文档：工具、GC、安全与诊断（一手）](https://docs.oracle.com/en/java/javase/25/)
- [Spring Framework 官方文档（一手）](https://docs.spring.io/spring-framework/reference/overview.html)
- [Spring Boot 官方文档（一手）](https://docs.spring.io/spring-boot/reference/index.html)
- [PostgreSQL 官方文档（一手）](https://www.postgresql.org/docs/current/index.html)
- 其余领域依据：[MIT 算法课程](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)、[OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/)、[Maven 生命周期](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)、[HTTP 语义（RFC 9110）](https://www.rfc-editor.org/rfc/rfc9110.html)、[Redis](https://redis.io/docs/latest/develop/)、[Kafka 设计](https://kafka.apache.org/42/design/design/)、[Raft](https://raft.github.io/)、[JUnit](https://docs.junit.org/current/user-guide/)、[Testcontainers](https://java.testcontainers.org/)、[OpenTelemetry](https://opentelemetry.io/docs/concepts/)、[JMH](https://github.com/openjdk/jmh)、[Spring Security](https://docs.spring.io/spring-security/reference/index.html)、[Java 安全编码指南](https://www.oracle.com/java/technologies/javase/seccodeguide.html)、[Kubernetes](https://kubernetes.io/docs/concepts/)、[GraalVM Native Image](https://www.graalvm.org/latest/reference-manual/native-image/)（均一手）

## Java 日志：从事件到采集的学习地图

**结论**：以 Java/Spring 服务端为范围，按「事件与级别 → API 与实现 → 正确记录与配置 → 生产采集、安全和性能 → 故障诊断」推进。Spring Boot Starter 默认用 Logback；应用可先掌握 SLF4J 与 Logback，再按实际依赖了解 JUL、System.Logger 和 Log4j 2。阶段划分及练习是学习建议，并非官方课程。

按事件来源区分五类日志：应用业务日志、HTTP 访问日志、框架/SQL 日志、JVM 日志与审计日志，各自的来源和用途不同。

| 阶段 | 学习内容 | 可验证产出 |
| --- | --- | --- |
| 1．事件基础 | 何时记日志；事件、级别、时间、来源、异常、上下文；日志与指标、链路追踪、审计的用途 | 对同一请求写出正常、失败、安全事件，说明级别与字段选择 |
| 2．API 与实现 | JUL、System.Logger、SLF4J；Provider、Logback/Log4j 2；依赖与单向桥接 | 画出从日志调用到输出的路径；排除缺 Provider、重复输出和桥接循环 |
| 3．应用写法与配置 | 参数化、异常原因链、MDC；层级、级别、Appender、Filter、Layout、Encoder | 按包调整级别；输出可检索事件与完整异常；验证 MDC 清理 |
| 4．生产链路 | JSON 字段模式、轮转与保留、容器输出、采集器、权限、脱敏、容量、异步队列 | 一条请求日志可按 traceId 定位；模拟磁盘/队列压力并观察丢失或阻塞 |
| 5．诊断与专项 | 日志缺失/重复/乱序、启动期配置、跨线程上下文、JVM `-Xlog`、审计日志 | 用证据定位一次日志故障；将 JVM GC 日志与应用事件区分 |

记录规则要点：按 TRACE/DEBUG/INFO/WARN/ERROR 选择级别；用参数化 `{}`、惰性参数、`Throwable` 末参或 `setCause`；避免同一异常在多层重复记录；日志内容可定位且不泄密。上下文用映射诊断上下文（Mapped Diagnostic Context，MDC）在请求范围设值与清理，并注意线程池、`CompletableFuture`、虚拟线程与响应式链路的上下文传播。

### 易错边界

- JUL 与 `System.Logger` 的参数格式用 `{0}`，SLF4J 用 `{}`；跨 API 搬代码必须改格式。
- SLF4J 2.x 通过 `ServiceLoader` 找 Provider，未找到时可能成为无操作日志；JUL→SLF4J 与 SLF4J→JUL 的桥接不能同时组成闭环。
- 参数化日志推迟消息格式化，但不推迟 Java 实参表达式求值；昂贵参数可用 SLF4J 2.x Fluent API 的 `Supplier`。`MDC.putCloseable` 关闭时移除键，不恢复同名键旧值。
- Spring Boot 3.4 起提供内置结构化日志格式；自定义 Logback 配置需采用对应 Encoder 才能使 `logging.structured.format.*` 生效。Logback `AsyncAppender` 默认可能在队列逼近满载时丢弃低级别事件。
- 应用日志与 JVM 统一日志的配置入口不同；GC 等 JVM 日志通过 `-Xlog` 控制。容器中优先掌握标准输出及平台的轮转、采集链路。

### 最小综合练习

用一个 Spring Boot 服务记录「签章请求接收、成功、失败」三类事件：配置包级日志级别和 JSON 控制台输出；用 MDC 或等价上下文附上请求关联 ID；失败事件保留异常堆栈，并验证日志中没有私钥、令牌或原文文档。随后分别测试线程池任务、异步队列压力和服务重启，检查关联字段、事件完整性与采集结果。签章业务字段及哪些事件属于正式审计，应再按项目适用规范确定。

信源：

- [JDK 21 JUL 概览（一手）](https://docs.oracle.com/en/java/javase/21/core/java-logging-overview.html)
- [SLF4J 手册（一手）](https://www.slf4j.org/manual.html)
- [SLF4J 错误说明（一手）](https://www.slf4j.org/codes.html)
- [SLF4J 桥接说明（一手）](https://www.slf4j.org/legacy.html)
- [Spring Boot 3.5 日志（一手）](https://docs.spring.io/spring-boot/3.5/reference/features/logging.html)
- [Spring Boot 3.4 发布说明（一手）](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.4-Release-Notes)
- [Logback 手册（一手）](https://logback.qos.ch/manual/)
- [Logback 异步 Appender（一手）](https://logback.qos.ch/manual/appenders-async-sift.html)
- [Log4j 2 架构（一手）](https://logging.apache.org/log4j/2.x/manual/architecture.html)
- [OpenTelemetry 日志模型（一手）](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [OWASP 日志指南（一手）](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

## JVM：规范、实现与运行时优化

本节合并两条记录：JVM 的系统学习路线，以及 Oracle 教程中「跨平台 + 运行时优化」原文的解释。

### 跨平台与 HotSpot 运行时优化

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

### 规范与实现的边界

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

### 关键边界

- JVM 规范的「方法区」是逻辑区域；HotSpot 元空间是实现中的类元数据存储，两者不能直接等同。JMM 约束多线程可观察行为，不是「堆和栈的分区图」。
- JVMS 第 5 章将 `static` 字段的默认值赋予准备阶段，将 `ConstantValue` 赋值与 `<clinit>` 放在初始化阶段；不要把口诀当成规范。
- GC 与诊断参数要按 JDK 版本核对；例如 JDK 21 的分代 ZGC 参数不能直接照搬到 JDK 25。

最小综合练习：在测试环境给同一个小型 Java 服务制造对象滞留、频繁分配、锁竞争及大量类加载四种现象；每次只改变一个条件；采集 GC 日志、JFR 与相应转储；写出「现象 → 证据 → 原因 → 调整 → 复测」，并记录 JDK、GC、堆参数、负载和测量窗口。只有当复测显示目标指标改善，才把调整视为有效。

信源：

- [Oracle Java Tutorials：About the Java Technology（一手，所引原文出处）](https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html)
- [JDK 21：HotSpot 性能增强（一手）](https://docs.oracle.com/en/java/javase/21/vm/java-hotspot-virtual-machine-performance-enhancements.html)
- [Java SE 27 JVM 规范（一手）](https://docs.oracle.com/javase/specs/jvms/se27/html/index.html)
- [Java SE 27 语言规范：线程与锁（一手）](https://docs.oracle.com/javase/specs/jls/se27/html/jls-17.html)
- [JDK 21 HotSpot GC 指南（一手）](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [JDK 21 虚拟机指南（一手）](https://docs.oracle.com/en/java/javase/21/vm/)
- [JDK 21 诊断工具（一手）](https://docs.oracle.com/en/java/javase/21/troubleshoot/diagnostic-tools.html)

## Java EE 与 Tomcat：规范与实现的关系

**结论**：Java 企业版（Java Platform, Enterprise Edition，Java EE，现 Jakarta EE）是一组规范，不是软件；Tomcat 是实现其中 Web 层子集（Servlet、JSP、EL、WebSocket）的开源 Servlet 容器。完整实现全部规范的软件叫应用服务器（如 GlassFish、WildFly、WebLogic）。Tomcat 听得多而 Java EE 听得少，因为：Tomcat 是可安装运行的具体产品、是 Web 子集的事实标准且被 Spring Boot 默认内嵌；「Java EE」之名已停用，完整平台话题又被 Spring 分流。

名称与归属演变：

```text
1999 Sun 发布 J2EE 1.2
  > 2006 J2EE 更名 Java EE（Java EE 5 起）
  > 2017 Oracle 将 Java EE 移交 Eclipse 基金会（EE4J 项目）
  > 2019 更名 Jakarta EE，首版 Jakarta EE 8 与 Java EE 8 规范一致
  > 2020 Jakarta EE 9 起，命名空间 javax 改为 jakarta
  > 2026 Tomcat 11 对应 Jakarta EE 11 的 Web 层规范
```

Tomcat 与规范版本对应：Tomcat 9 对应 Java EE 8（Servlet 4.0，最后一个支持 `javax` 命名空间的大版本）；Tomcat 10.1 对应 Jakarta EE 10（Servlet 6.0）；Tomcat 11 对应 Jakarta EE 11（Servlet 6.1）。学习方向应按实际工程需求选择。

信源：

- [Apache Tomcat 版本与规范对应（一手）](https://tomcat.apache.org/whichversion.html)
- [Jakarta EE 官网（一手）](https://jakarta.ee/)
- [Jakarta EE About（一手）](https://jakarta.ee/about/)
- [Eclipse Foundation 博客：Java EE Moves to the Eclipse Foundation（一手，2017-09-12）](https://eclipse-foundation.blog/2017/09/12/java-ee-moves-to-the-eclipse-foundation)
