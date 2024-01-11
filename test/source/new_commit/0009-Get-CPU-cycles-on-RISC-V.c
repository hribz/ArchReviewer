From df20eb17a10aa4c930887c92a4d5a3832402a096 Mon Sep 17 00:00:00 2001
From: "v.v.mitrofanov" <v.v.mitrofanov@yadro.com>
Date: Mon, 31 Jan 2022 13:41:30 +0300
Subject: [PATCH 2/2] Get CPU cycles on RISC-V

This test acquires CPU cycles to perform output calculations
and get timestamps. There is no cpu_cycles() implementation on RISC-V arch.

This patch gets cycles using perf events.
One of the most notable reasons to use perf event instead of
reading counter registers is to avoid modifying MUCOUNTEREN
register. Due to the RISC-V ISA specification (riscv-privileged-v1.9)
before getting any access to counter registers it is necessary to enable it in MUCOUNTEREN in a privileged mode. On the other hand,
perf events are free to use.

This patch is tested on the SiFive HiFive Unmatched board.

Signed-off-by: v.v.mitrofanov <v.v.mitrofanov@yadro.com>
---
 src/get_clock.c | 62 +++++++++++++++++++++++++++++++++++++++++++++++++
 src/get_clock.h |  9 +++++++
 2 files changed, 71 insertions(+)

diff --git a/src/get_clock.c b/src/get_clock.c
index 78ad865..c6adbdc 100755
--- a/src/get_clock.c
+++ b/src/get_clock.c
@@ -237,3 +237,65 @@ double get_cpu_mhz(int no_cpu_freq_warn)
 	return proc;
 #endif
 }
+
+#if defined(__riscv)
+#include <stdlib.h>
+#include <stdio.h>
+#include <unistd.h>
+#include <string.h>
+#include <sys/syscall.h>
+#include <linux/perf_event.h>
+#include <asm/unistd.h>
+
+static long perf_event_open(struct perf_event_attr *hw_event,
+		pid_t pid, int cpu, int group_fd,
+		unsigned long flags)
+{
+	return syscall(__NR_perf_event_open, hw_event, pid,
+			cpu, group_fd, flags);
+}
+
+cycles_t perf_get_cycles()
+{
+	cycles_t cycles = 0;
+	struct perf_event_attr pe;
+	const pid_t pid = 0;		// Current task
+	const int cpu = -1;  		// On any CPU
+	const int group_fd = -1;	// Use leader group
+	const unsigned long flags = 0;
+	/* Use this variable just to open perf event here and once.
+	   It is appropriate because it touches only this function and
+	   not fix other code */
+	static int is_open = 0;
+	/* Make file discriptor static just to keep it valid during
+	   programm execution. It will be closed automatically when
+	   test finishes. It is a hack just not to fix other part of test */
+        static int fd = -1;
+
+	if (!is_open) {
+		memset(&pe, 0, sizeof(pe));
+
+		pe.type = PERF_TYPE_HARDWARE;
+		pe.size = sizeof(pe);
+		pe.config = PERF_COUNT_HW_CPU_CYCLES;
+		pe.disabled = 0;
+		pe.exclude_kernel = 0;
+		pe.exclude_hv = 0;
+
+		fd = perf_event_open(&pe, pid, cpu, group_fd, flags);
+		if (fd == -1) {
+			fprintf(stderr, "Error opening perf event (%llx)\n", pe.config);
+			exit(EXIT_FAILURE);
+		}
+
+		is_open = 1;
+	}
+
+	if(read(fd, &cycles, sizeof(cycles)) < 0) {
+		fprintf(stderr, "Error reading perf event (%llx)\n", pe.config);
+		exit(EXIT_FAILURE);
+	}
+
+	return cycles;
+}
+#endif
diff --git a/src/get_clock.h b/src/get_clock.h
index dacbcd0..97c3500 100755
--- a/src/get_clock.h
+++ b/src/get_clock.h
@@ -104,6 +104,15 @@ static inline cycles_t get_cycles()
 	asm volatile("mrs %0, cntvct_el0" : "=r" (cval));
 	return cval;
 }
+#elif defined(__riscv)
+typedef unsigned long cycles_t;
+
+cycles_t perf_get_cycles();
+
+static inline cycles_t get_cycles()
+{
+	return perf_get_cycles();
+}
 
 #elif defined(__loongarch64)
 typedef unsigned long cycles_t;
-- 
2.40.1

