# Meeting 1

> May 11, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1683814881754659 

1. Highlights
    - Weekly meeting if possible (Thu)
    - Changes on the schedule/work items (To be discussed)
    - The proposal aims to work on an overall performance framework, whereas the original initiative is to identify performance changes when a single SecRule is updated (e.g., regex changes). We will focus on a single SecRule first, which can be extended to an overall performance test.
    - The initiative of the framework is to be flexible enough to adapt to other WAFs (e.g., Coraza). In the first stage, We will start with ModSecurity 2.9.
    - As a public-facing application, testing the functionality is essential. (Adds into the schedule)

2. Ideas
    - Performance tests cannot rely on a single payload. Fuzzing might be a good way to yield multiple payloads to support the test
    - Before the development, defining the matrix we want is necessary. Meanwhile, we also need to consider what matrix/data we can get.

3. To-dos
    - Review/update the proposals.
    - Establish a work environment. (ModSecurity 2.9)
    - Research on existing performance testing framework.
    - Reading documentations.

# Meeting 2

> May 25, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1685040293587099

1. Progress
    - [x] [#1](https://github.com/dextermallo/GSoC-2023/issues/1) Review and update the proposals
    - [x] [#2](https://github.com/dextermallo/GSoC-2023/issues/2) Establish a work environment
    - [ ] [#3](https://github.com/dextermallo/GSoC-2023/issues/3) Research on existing performance testing framework (`WIP`: collect some sources but yet to read)
    - [ ] Reading documentation (CRS/go-ftw) (`WIP`: learning some args and workflow)
    - [x] Reading some suggestions for GSoC and other community topics 
    - [x] A draft of the framework (under discussion)

2. Findings & Ideas
    - N/A

3. Impediments
    - The complexity of implementing CRS with services. (e.g., different ways to configure. When I attempted to remove a SecRule from ModSecurity v3 using nginx, I found multiple ways from the Internet but none of them worked, such as modifying nginx.conf or crs-setup.conf. Keep working on it.)

4. Others
    - review/add contexts for attempts to remove a SecRule from ModSecurity v3 using nginx. (since issues happened on nginx recently as well)
    - Focus on one feature at a time.
    - Applying integration into the existing utility (go-ftw) might not be a good idea. Although less wheel-rebuild, the complexity and purity (functionality) will be affected.
    - The framework is way more important than tech details.

5. Next Actions
    - Continue researching other approaches (benchmarking in the same container; using another container to test the WAF container; server-side testing)
    - Update the proposal
    - Clarify/refine the draft of the framework
    - Research more about different matrix/matrix collection

# Meeting 3

> Jun 1, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1685631723419749

1. Progress
    - [x] [#3](https://github.com/dextermallo/GSoC-2023/issues/3) Continue researching other approaches (benchmarking in the same container; using another container to test the WAF container; server-side testing)
    - [x] [#3](https://github.com/dextermallo/GSoC-2023/issues/3) Clarify/refine the draft of the framework
    - [x] [#3](https://github.com/dextermallo/GSoC-2023/issues/3) Research more about different matrix/matrix collection

2. Impediments

- The PoC to evaluate performance before/after a rule change seems not obvious (@rx to !@rx), looking for better changes. (suggested by Christian: take any complex regex and replace it with a simple very version)

3. Others

- Define the scope: discussion regarding the matrices we can collect currently and other possible matrices
- Concerns for log analysis: log analysis may encounter challenges, like log format may differ among platforms (ModSec v2 and v3) and accuracy concerns. 
- Accuracy: the behaviour of evaluating performance itself affects the performance. Nonetheless, as the framework is to evaluate the performance change, the accuracy issue can be addressed later on.

4. Next Actions

- Research on other server-side testing approaches (e.g., kernel-level or 3rd party tools like Prometheus)
- Continue working on PoC (both client-side and server-side)
- Check the existing log settings for CRS (e.g., can the log be set to milliseconds?)
- Research if there are other matrices we can collect (e.g., low-level matrices)

# Meeting 4

> Jun 8, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1686240412879279

1. Progress

- [x] [[#3]](https://github.com/dextermallo/GSoC-2023/issues/3) Research other server-side testing approaches: Prometheus/Elasticsearch/sysdig
- [x] Continue working on PoC: test on another rule
- [x] [[#4]](https://github.com/dextermallo/GSoC-2023/issues/4) Check the existing log settings for CRS (e.g., can the log be set to milliseconds?)
- [x] [[#5]](https://github.com/dextermallo/GSoC-2023/issues/5) Research if there are other matrices we can collect (e.g., low-level matrices): syscall; some literature review
- [x] [[#3]](https://github.com/dextermallo/GSoC-2023/issues/3#issuecomment-1581217483) redraft proposal with sidecar pattern
- [x] [[coreruleset#3232]](https://github.com/coreruleset/coreruleset/pull/3232) A PR for CRS documentation

2. Others

- Suggestions for log analysis: use audit_log instead of debug_log
- Framework with sidecar pattern can be refined with more details: rephrase the components (high-level) and define the interface. (e.g., two log components and one report component phrase the data in different formats. A user can query from the report component to get the performance data)

3. Next Actions

- Research on audit_log (ModSec v2)
- Refine the framework with high-level components and interfaces
- Research for some feedback (concurrency issue, methodology for cross-platform evaluation, etc.)

# Meeting 5

> Jun 15, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1686850982091809

1. Progress

- [ ] Research on audit_log (ModSec v2): didn't have time to look into it :(
- [x] Refine the framework with high-level components and interfaces: changing terms to high-level items; adding new components and matrices.
- [x] Research for some feedback (concurrency issue, methodology for cross-platform evaluation, etc.): done some research on eBPF and added it into the framework (host-level collector)

2. Others

- A merit contributed by the framework is that a user can integrate any kind of 3rd-party utils into the framework easily. Specifically, they only need to implement a data parser and follow the predefined interface for the integrations.
- A suggestion for a PoC testing (I am testing on some regex changes): Load a single rule at a time for testing

3. Next Actions

- A PoC to test the framework. Especially, interfaces, a data parser and a server-side collector to test the pipeline. 
- Initialise testing libs for the performance framework (e.g., pytest)

# Meeting 6

> Jun 22, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1687444119818669

1. Progress

- [x] A PoC to test the framework. Especially interfaces, a data parser and a server-side collector to test the pipeline
    - Implemented two data collectors (go-ftw and cAdvisor), Interfaces, Parsers, and an interactive visualizer (matplotlib)
    - Repo: https://github.com/dextermallo/GSoC-2023/tree/feat/poc-data-collector
- [x] Initialise testing libs for the performance framework (e.g., pytest): using poetry to manage dependencies & version

2. Next Actions

- Optimize visualizer (e.g., adding x-label, y-label, data dots which show details when hovering on them, etc.)
- Adding documentation, test cases, and test coverage
- Implement new data listeners (eBPF)
- Check on `go-ftw  -o` to see if possible to replace regex for parsing raw data from go-ftw

# Meeting 7

> Jun 29, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1688074621676979

1. Progress

- [x] Optimize visualizer (e.g., adding x-label, y-label, data dots which show details when hovering on them, etc.): continue
- [x] Adding documentation, test cases, and test coverage: current coverage is 91%
    ![meeting-7-test-coverage](./assets/meeting-7-test-coverage.png)
- [ ] Implement new data listeners (eBPF)
- [x] Check on `go-ftw  -o` to see if possible to replace regex for parsing raw data from go-ftw: the data only contains runtime (no RTT), but it is superior to parse the data.

2. Next Actions

- Usage documentation
- Check on GitHub summary/pipeline integration
- Other util integration (eBPF)
- Further research on data visualization

# Meeting 8

> Jul 13, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1688074621676979

1. Progress

- [x] Usage documentation: https://github.com/dextermallo/GSoC-2023/blob/feat/poc-data-collector/src/README.md
- [x] Check on GitHub summary/pipeline integration: Done a PoC (https://github.com/dextermallo/GSoC-2023/actions)
- [x] Other utils integration (eBPF): A PoC of eBPF using dynamic probes (pre-built  tracepoints)
- [ ] Further research on data visualization: TBD

2. Discussion

- The direction of the util: Should it be pipeline-based or interactive-based?
    - Christian: Both are important. Interactive-based is essential for local usage, which is much more convenient for developers. Pipeline-based is for CI/CD, which is convenient for maintainers.
- For pipeline-based, how should we design the threshold?
    - Felipe/Christian: as long as a threshold is defined on "each rule", they can be adjusted/fine-tuned.
- Next milestone: what is the next step for the framework? While most of the PoC is implemented, how can people use/maintain it in the future?
    - Christian: it is important to discuss these items as the GSoC is a short-term project.
- Some interesting stories behind the CoreRuleSet shared by Christian

3. Next Actions

- Fully automated the current implementation
- To be tested: Does VM for GitHub Action supports eBPF?
- Redesign the architecture for the framework to support both interactive and pipeline-based
- Integrate the concept of "threshold" into the architecture
- Discuss/Draft 2-nd phase objective/goals

# Regular updates

> Jul 20, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1689861012777359

1. Progress

- [x] Fully automated the current implementation: Done
- [x] Redesign the architecture for the framework to support both interactive and pipeline-based
- [x] Integrate the concept of "threshold" into the architecture
- [ ] Discuss/Draft 2-nd phase objective/goals: WIP
- [ ] To be tested: Does VM for GitHub Action supports eBPF?: TBD

2. Next Actions

- Discuss/Draft 2nd phase objective/goals (Cont.)
- Bug/Changes from previous comments.
- Create reports for cAdvisor/locust.
- Add threshold for cAdvisor/locust

# Meeting 9

> Jul 27, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1690464215034819

1. Progress

- [x] Finalize 2nd phase objective/goals
- [x] Bug/Changes from previous comments
- [x] Create reports for cAdvisor/locust
- [x] Add threshold configurations for cAdvisor/locust

2. Next Actions
- Update test cases
- Integrate into GitHub Action
- Fine-tune output/blocking for pipelines
- Documentation

# Regular updates

> Aug 3, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1691091689381609

1. Progress
- [ ] Update test cases: working on integration test
- [x] Integrate into GitHub Action: go-ftw completed [(link)](https://github.com/dextermallo/GSoC-2023/actions/runs/5716710386), cAdvisor has an OS issue (WIP)
- [x] Fine-tune output/blocking for pipelines: looking for better utils that can put summary as comments directly
- [x] Documentation: WIP

2. Next Actions
- Update test cases
- Integrate into GitHub Action
- Fine-tune output/blocking for pipelines
- Documentation

# Meeting 10

> Aug 10, 2023
>
> Thread: 

1. Progress
- [x] Update test cases (Continue)
- [x] Integrate into GitHub Action: locust and ftw completed, cAdvisor requires gcr, which is not supported by GitHub Action (On-hold)
- [x] Fine-tune output/blocking for pipelines
- [x] Code Documentation
- [x] Updates for the roadmaps for the framework ((link))[https://github.com/dextermallo/GSoC-2023/issues/9]

2. Next Actions
- Documentation: Tutorial, Usage, etc.
- Plans for project migration.
- Test cases (Continue)

# Meeting 11

> Aug 17, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1691674261119029

1. Progress
- Documentation: Tutorial, Usage, etc.
- Plans for project migration.

2. Next Actions
- Wrapping up! Review and continue to update the documentation.
- Discuss the project migration and the new name for the repo.
