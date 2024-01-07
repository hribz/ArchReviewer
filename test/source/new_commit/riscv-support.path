From f45a2a59119c9a2dda0ab7f58d61f5ea64589411 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:06 +0800
Subject: [PATCH 1/9] Add RISCV64 framework code support

This patch mainly added some environment configurations, macro definitions,
specific architecture structures and some function declarations supported
by the RISCV64 architecture.

We can use the build command to get the simplest version crash tool:
	make target=RISCV64 -j2

Co-developed-by: Lifang Xia <lifang_xia@linux.alibaba.com>
Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 Makefile            |   7 +-
 README              |   6 +-
 configure.c         |  43 ++++++++++++-
 defs.h              | 154 +++++++++++++++++++++++++++++++++++++++++++-
 diskdump.c          |  11 +++-
 help.c              |   6 +-
 lkcd_vmdump_v1.h    |   8 +--
 lkcd_vmdump_v2_v3.h |   8 +--
 netdump.c           |   9 ++-
 ramdump.c           |   2 +
 riscv64.c           |  54 ++++++++++++++++
 symbols.c           |  10 +++
 12 files changed, 294 insertions(+), 24 deletions(-)
 create mode 100644 riscv64.c

diff --git a/Makefile b/Makefile
index 79aef17..1506dd4 100644
--- a/Makefile
+++ b/Makefile
@@ -64,7 +64,7 @@ CFILES=main.c tools.c global_data.c memory.c filesys.c help.c task.c \
 	kernel.c test.c gdb_interface.c configure.c net.c dev.c bpf.c \
 	printk.c \
 	alpha.c x86.c ppc.c ia64.c s390.c s390x.c s390dbf.c ppc64.c x86_64.c \
-	arm.c arm64.c mips.c mips64.c sparc64.c \
+	arm.c arm64.c mips.c mips64.c riscv64.c sparc64.c \
 	extensions.c remote.c va_server.c va_server_v1.c symbols.c cmdline.c \
 	lkcd_common.c lkcd_v1.c lkcd_v2_v3.c lkcd_v5.c lkcd_v7.c lkcd_v8.c\
 	lkcd_fix_mem.c s390_dump.c lkcd_x86_trace.c \
@@ -84,7 +84,7 @@ OBJECT_FILES=main.o tools.o global_data.o memory.o filesys.o help.o task.o \
 	build_data.o kernel.o test.o gdb_interface.o net.o dev.o bpf.o \
 	printk.o \
 	alpha.o x86.o ppc.o ia64.o s390.o s390x.o s390dbf.o ppc64.o x86_64.o \
-	arm.o arm64.o mips.o mips64.o sparc64.o \
+	arm.o arm64.o mips.o mips64.o riscv64.o sparc64.o \
 	extensions.o remote.o va_server.o va_server_v1.o symbols.o cmdline.o \
 	lkcd_common.o lkcd_v1.o lkcd_v2_v3.o lkcd_v5.o lkcd_v7.o lkcd_v8.o \
 	lkcd_fix_mem.o s390_dump.o netdump.o diskdump.o makedumpfile.o xendump.o \
@@ -438,6 +438,9 @@ mips.o: ${GENERIC_HFILES} ${REDHAT_HFILES} mips.c
 mips64.o: ${GENERIC_HFILES} ${REDHAT_HFILES} mips64.c
 	${CC} -c ${CRASH_CFLAGS} mips64.c ${WARNING_OPTIONS} ${WARNING_ERROR}
 
+riscv64.o: ${GENERIC_HFILES} ${REDHAT_HFILES} riscv64.c
+	${CC} -c ${CRASH_CFLAGS} riscv64.c ${WARNING_OPTIONS} ${WARNING_ERROR}
+
 sparc64.o: ${GENERIC_HFILES} ${REDHAT_HFILES} sparc64.c
 	${CC} -c ${CRASH_CFLAGS} sparc64.c ${WARNING_OPTIONS} ${WARNING_ERROR}
 
diff --git a/README b/README
index 1f98fbf..9850a29 100644
--- a/README
+++ b/README
@@ -37,8 +37,8 @@
   These are the current prerequisites: 
 
   o  At this point, x86, ia64, x86_64, ppc64, ppc, arm, arm64, alpha, mips,
-     mips64, s390 and s390x-based kernels are supported.  Other architectures
-     may be addressed in the future.
+     mips64, riscv64, s390 and s390x-based kernels are supported.  Other
+     architectures may be addressed in the future.
 
   o  One size fits all -- the utility can be run on any Linux kernel version
      version dating back to 2.2.5-15.  A primary design goal is to always
@@ -98,6 +98,8 @@
      arm64 dumpfiles may be built by typing "make target=ARM64".
   o  On an x86_64 host, an x86_64 binary that can be used to analyze
      ppc64le dumpfiles may be built by typing "make target=PPC64".
+  o  On an x86_64 host, an x86_64 binary that can be used to analyze
+     riscv64 dumpfiles may be built by typing "make target=RISCV64".
 
   Traditionally when vmcores are compressed via the makedumpfile(8) facility
   the libz compression library is used, and by default the crash utility
diff --git a/configure.c b/configure.c
index 5188851..08b52be 100644
--- a/configure.c
+++ b/configure.c
@@ -107,6 +107,7 @@ void add_extra_lib(char *);
 #undef MIPS
 #undef SPARC64
 #undef MIPS64
+#undef RISCV64
 
 #define UNKNOWN 0
 #define X86     1
@@ -122,6 +123,7 @@ void add_extra_lib(char *);
 #define MIPS    11
 #define SPARC64 12
 #define MIPS64  13
+#define RISCV64 14
 
 #define TARGET_X86    "TARGET=X86"
 #define TARGET_ALPHA  "TARGET=ALPHA"
@@ -136,6 +138,7 @@ void add_extra_lib(char *);
 #define TARGET_MIPS   "TARGET=MIPS"
 #define TARGET_MIPS64 "TARGET=MIPS64"
 #define TARGET_SPARC64 "TARGET=SPARC64"
+#define TARGET_RISCV64 "TARGET=RISCV64"
 
 #define TARGET_CFLAGS_X86    "TARGET_CFLAGS=-D_FILE_OFFSET_BITS=64"
 #define TARGET_CFLAGS_ALPHA  "TARGET_CFLAGS="
@@ -158,6 +161,8 @@ void add_extra_lib(char *);
 #define TARGET_CFLAGS_MIPS_ON_X86_64  "TARGET_CFLAGS=-m32 -D_FILE_OFFSET_BITS=64"
 #define TARGET_CFLAGS_MIPS64          "TARGET_CFLAGS="
 #define TARGET_CFLAGS_SPARC64         "TARGET_CFLAGS="
+#define TARGET_CFLAGS_RISCV64         "TARGET_CFLAGS="
+#define TARGET_CFLAGS_RISCV64_ON_X86_64	"TARGET_CFLAGS="
 
 #define GDB_TARGET_DEFAULT        "GDB_CONF_FLAGS="
 #define GDB_TARGET_ARM_ON_X86     "GDB_CONF_FLAGS=--target=arm-elf-linux"
@@ -168,6 +173,7 @@ void add_extra_lib(char *);
 #define GDB_TARGET_PPC64_ON_X86_64  "GDB_CONF_FLAGS=--target=powerpc64le-unknown-linux-gnu"
 #define GDB_TARGET_MIPS_ON_X86     "GDB_CONF_FLAGS=--target=mipsel-elf-linux"
 #define GDB_TARGET_MIPS_ON_X86_64  "GDB_CONF_FLAGS=--target=mipsel-elf-linux CFLAGS=-m32 CXXFLAGS=-m32"
+#define GDB_TARGET_RISCV64_ON_X86_64  "GDB_CONF_FLAGS=--target=riscv64-unknown-linux-gnu"
      
 /*
  *  The original plan was to allow the use of a particular version
@@ -404,6 +410,9 @@ get_current_configuration(struct supported_gdb_version *sp)
 #ifdef __sparc_v9__
 	target_data.target = SPARC64;
 #endif
+#if defined(__riscv) && (__riscv_xlen == 64)
+	target_data.target = RISCV64;
+#endif
 
 	set_initial_target(sp);
 
@@ -457,6 +466,12 @@ get_current_configuration(struct supported_gdb_version *sp)
 			if ((target_data.initial_gdb_target != UNKNOWN) &&
 			    (target_data.host != target_data.initial_gdb_target))
 				arch_mismatch(sp);
+		} else if ((target_data.target == X86_64) &&
+			(name_to_target((char *)target_data.target_as_param) == RISCV64)) {
+			/*
+			 *  Build an RISCV64 crash binary on an X86_64 host.
+			 */
+			target_data.target = RISCV64;
 		} else {
 			fprintf(stderr,
 			    "\ntarget=%s is not supported on the %s host architecture\n\n",
@@ -497,6 +512,14 @@ get_current_configuration(struct supported_gdb_version *sp)
 		    (target_data.target != MIPS64))
 			arch_mismatch(sp);
 
+		if ((target_data.initial_gdb_target == RISCV64) &&
+		    (target_data.target != RISCV64)) {
+			if (target_data.target == X86_64)
+				target_data.target = RISCV64;
+			else
+				arch_mismatch(sp);
+		}
+
 		if ((target_data.initial_gdb_target == X86) &&
 		    (target_data.target != X86)) {
 			if (target_data.target == X86_64) 
@@ -660,6 +683,9 @@ show_configuration(void)
 	case SPARC64:
 		printf("TARGET: SPARC64\n");
 		break;
+	case RISCV64:
+		printf("TARGET: RISCV64\n");
+		break;
 	}
 
 	if (strlen(target_data.program)) {
@@ -777,6 +803,14 @@ build_configure(struct supported_gdb_version *sp)
 		target = TARGET_SPARC64;
 		target_CFLAGS = TARGET_CFLAGS_SPARC64;
 		break;
+	case RISCV64:
+		target = TARGET_RISCV64;
+		if (target_data.host == X86_64) {
+			target_CFLAGS = TARGET_CFLAGS_RISCV64_ON_X86_64;
+			gdb_conf_flags = GDB_TARGET_RISCV64_ON_X86_64;
+		} else
+			target_CFLAGS = TARGET_CFLAGS_RISCV64;
+		break;
 	}
 
 	ldflags = get_extra_flags("LDFLAGS.extra", NULL);
@@ -1374,7 +1408,7 @@ make_spec_file(struct supported_gdb_version *sp)
 	printf("Vendor: Red Hat, Inc.\n");
 	printf("Packager: Dave Anderson <anderson@redhat.com>\n");
 	printf("ExclusiveOS: Linux\n");
-	printf("ExclusiveArch: %%{ix86} alpha ia64 ppc ppc64 ppc64pseries ppc64iseries x86_64 s390 s390x arm aarch64 ppc64le mips mipsel mips64el sparc64\n");
+	printf("ExclusiveArch: %%{ix86} alpha ia64 ppc ppc64 ppc64pseries ppc64iseries x86_64 s390 s390x arm aarch64 ppc64le mips mipsel mips64el sparc64 riscv64\n");
 	printf("Buildroot: %%{_tmppath}/%%{name}-root\n");
 	printf("BuildRequires: ncurses-devel zlib-devel bison\n");
 	printf("Requires: binutils\n");
@@ -1613,6 +1647,8 @@ set_initial_target(struct supported_gdb_version *sp)
 		target_data.initial_gdb_target = MIPS;
 	else if (strncmp(buf, "SPARC64", strlen("SPARC64")) == 0)
 		target_data.initial_gdb_target = SPARC64;
+	else if (strncmp(buf, "RISCV64", strlen("RISCV64")) == 0)
+		target_data.initial_gdb_target = RISCV64;
 }
 
 char *
@@ -1633,6 +1669,7 @@ target_to_name(int target)
 	case MIPS:   return("MIPS");
 	case MIPS64: return("MIPS64");
 	case SPARC64: return("SPARC64");
+	case RISCV64: return("RISCV64");
 	}
 
 	return "UNKNOWN";
@@ -1697,6 +1734,10 @@ name_to_target(char *name)
 		return MIPS64;
 	else if (strncmp(name, "sparc64", strlen("sparc64")) == 0)
 		return SPARC64;
+	else if (strncmp(name, "RISCV64", strlen("RISCV64")) == 0)
+		return RISCV64;
+	else if (strncmp(name, "riscv64", strlen("riscv64")) == 0)
+		return RISCV64;
 
 	return UNKNOWN;
 }
diff --git a/defs.h b/defs.h
index afdcf6c..d715378 100644
--- a/defs.h
+++ b/defs.h
@@ -76,7 +76,7 @@
 #if !defined(X86) && !defined(X86_64) && !defined(ALPHA) && !defined(PPC) && \
     !defined(IA64) && !defined(PPC64) && !defined(S390) && !defined(S390X) && \
     !defined(ARM) && !defined(ARM64) && !defined(MIPS) && !defined(MIPS64) && \
-    !defined(SPARC64)
+    !defined(RISCV64) && !defined(SPARC64)
 #ifdef __alpha__
 #define ALPHA
 #endif
@@ -118,6 +118,9 @@
 #ifdef __sparc_v9__
 #define SPARC64
 #endif
+#if defined(__riscv) && (__riscv_xlen == 64)
+#define RISCV64
+#endif
 #endif
 
 #ifdef X86
@@ -159,6 +162,9 @@
 #ifdef SPARC64
 #define NR_CPUS  (4096)
 #endif
+#ifdef RISCV64
+#define NR_CPUS  (256)
+#endif
 
 #define NR_DEVICE_DUMPS (64)
 
@@ -3484,6 +3490,63 @@ struct arm64_stackframe {
 #define _MAX_PHYSMEM_BITS       48
 #endif  /* MIPS64 */
 
+#ifdef RISCV64
+#define _64BIT_
+#define MACHINE_TYPE		"RISCV64"
+
+/*
+ * Direct memory mapping
+ */
+#define PTOV(X) 									\
+	(((unsigned long)(X)+(machdep->kvbase)) - machdep->machspec->phys_base)
+#define VTOP(X) ({									\
+	ulong _X = X;									\
+	(THIS_KERNEL_VERSION >= LINUX(5,13,0) &&					\
+		(_X) >= machdep->machspec->kernel_link_addr) ?				\
+		(((unsigned long)(_X)-(machdep->machspec->kernel_link_addr)) +		\
+		 machdep->machspec->phys_base):						\
+		(((unsigned long)(_X)-(machdep->kvbase)) +				\
+		 machdep->machspec->phys_base);						\
+	})
+#define PAGEBASE(X)		(((ulong)(X)) & (ulong)machdep->pagemask)
+
+/*
+ * Stack size order
+ */
+#define THREAD_SIZE_ORDER	2
+
+#define PAGE_OFFSET		(machdep->machspec->page_offset)
+#define VMALLOC_START		(machdep->machspec->vmalloc_start_addr)
+#define VMALLOC_END		(machdep->machspec->vmalloc_end)
+#define VMEMMAP_VADDR		(machdep->machspec->vmemmap_vaddr)
+#define VMEMMAP_END		(machdep->machspec->vmemmap_end)
+#define MODULES_VADDR		(machdep->machspec->modules_vaddr)
+#define MODULES_END		(machdep->machspec->modules_end)
+#define IS_VMALLOC_ADDR(X)	riscv64_IS_VMALLOC_ADDR((ulong)(X))
+
+/* from arch/riscv/include/asm/pgtable.h */
+#define __SWP_TYPE_SHIFT	6
+#define __SWP_TYPE_BITS 	5
+#define __SWP_TYPE_MASK 	((1UL << __SWP_TYPE_BITS) - 1)
+#define __SWP_OFFSET_SHIFT	(__SWP_TYPE_BITS + __SWP_TYPE_SHIFT)
+
+#define MAX_SWAPFILES_CHECK()	BUILD_BUG_ON(MAX_SWAPFILES_SHIFT > __SWP_TYPE_BITS)
+
+#define SWP_TYPE(entry) 	(((entry) >> __SWP_TYPE_SHIFT) & __SWP_TYPE_MASK)
+#define SWP_OFFSET(entry)	((entry) >> __SWP_OFFSET_SHIFT)
+#define __swp_type(entry)	SWP_TYPE(entry)
+#define __swp_offset(entry)	SWP_OFFSET(entry)
+
+#define TIF_SIGPENDING		(THIS_KERNEL_VERSION >= LINUX(2,6,23) ? 1 : 2)
+
+/* from arch/riscv/include/asm/sparsemem.h */
+#define _SECTION_SIZE_BITS	27
+#define _MAX_PHYSMEM_BITS	56 /* 56-bit physical address supported */
+#define PHYS_MASK_SHIFT 	_MAX_PHYSMEM_BITS
+#define PHYS_MASK		(((1UL) << PHYS_MASK_SHIFT) - 1)
+
+#endif  /* RISCV64 */
+
 #ifdef X86
 #define _32BIT_
 #define MACHINE_TYPE       "X86"
@@ -4532,6 +4595,10 @@ struct machine_specific {
 #define MAX_HEXADDR_STRLEN (16)
 #define UVADDR_PRLEN      (16)
 #endif
+#ifdef RISCV64
+#define MAX_HEXADDR_STRLEN (16)
+#define UVADDR_PRLEN       (16)
+#endif
 
 #define BADADDR  ((ulong)(-1))
 #define BADVAL   ((ulong)(-1))
@@ -5127,6 +5194,9 @@ void dump_build_data(void);
 #ifdef MIPS64
 #define machdep_init(X) mips64_init(X)
 #endif
+#ifdef RISCV64
+#define machdep_init(X) riscv64_init(X)
+#endif
 #ifdef SPARC64
 #define machdep_init(X) sparc64_init(X)
 #endif
@@ -5607,6 +5677,9 @@ void display_help_screen(char *);
 #ifdef SPARC64
 #define dump_machdep_table(X) sparc64_dump_machdep_table(X)
 #endif
+#ifdef RISCV64
+#define dump_machdep_table(X) riscv64_dump_machdep_table(X)
+#endif
 extern char *help_pointer[];
 extern char *help_alias[];
 extern char *help_ascii[];
@@ -6684,6 +6757,85 @@ struct machine_specific {
 
 #endif /* MIPS64 */
 
+/*
+ * riscv64.c
+ */
+void riscv64_display_regs_from_elf_notes(int, FILE *);
+
+#ifdef RISCV64
+void riscv64_init(int);
+void riscv64_dump_machdep_table(ulong);
+int riscv64_IS_VMALLOC_ADDR(ulong);
+
+#define display_idt_table() \
+	error(FATAL, "-d option is not applicable to RISCV64 architecture\n")
+
+/* from arch/riscv/include/asm/ptrace.h */
+struct riscv64_register {
+	ulong regs[36];
+};
+
+struct riscv64_pt_regs {
+	ulong badvaddr;
+	ulong cause;
+	ulong epc;
+};
+
+struct riscv64_unwind_frame {
+	ulong fp;
+	ulong sp;
+	ulong pc;
+};
+
+#define KSYMS_START	(0x1)
+
+struct machine_specific {
+	ulong phys_base;
+	ulong page_offset;
+	ulong vmalloc_start_addr;
+	ulong vmalloc_end;
+	ulong vmemmap_vaddr;
+	ulong vmemmap_end;
+	ulong modules_vaddr;
+	ulong modules_end;
+	ulong kernel_link_addr;
+
+	ulong _page_present;
+	ulong _page_read;
+	ulong _page_write;
+	ulong _page_exec;
+	ulong _page_user;
+	ulong _page_global;
+	ulong _page_accessed;
+	ulong _page_dirty;
+	ulong _page_soft;
+
+	ulong _pfn_shift;
+
+	struct riscv64_register *crash_task_regs;
+};
+/* from arch/riscv/include/asm/pgtable-bits.h */
+#define _PAGE_PRESENT	(machdep->machspec->_page_present)
+#define _PAGE_READ	(machdep->machspec->_page_read)
+#define _PAGE_WRITE	(machdep->machspec->_page_write)
+#define _PAGE_EXEC	(machdep->machspec->_page_exec)
+#define _PAGE_USER	(machdep->machspec->_page_user)
+#define _PAGE_GLOBAL	(machdep->machspec->_page_global)
+#define _PAGE_ACCESSED	(machdep->machspec->_page_accessed)
+#define _PAGE_DIRTY	(machdep->machspec->_page_dirty)
+#define _PAGE_SOFT	(machdep->machspec->_page_soft)
+#define _PAGE_SEC	(machdep->machspec->_page_sec)
+#define _PAGE_SHARE	(machdep->machspec->_page_share)
+#define _PAGE_BUF	(machdep->machspec->_page_buf)
+#define _PAGE_CACHE	(machdep->machspec->_page_cache)
+#define _PAGE_SO	(machdep->machspec->_page_so)
+#define _PAGE_SPECIAL	_PAGE_SOFT
+#define _PAGE_TABLE	_PAGE_PRESENT
+#define _PAGE_PROT_NONE _PAGE_READ
+#define _PAGE_PFN_SHIFT 10
+
+#endif /* RISCV64 */
+
 /*
  * sparc64.c
  */
diff --git a/diskdump.c b/diskdump.c
index 2c1f9be..28503bc 100644
--- a/diskdump.c
+++ b/diskdump.c
@@ -622,6 +622,9 @@ restart:
 	else if (STRNEQ(header->utsname.machine, "aarch64") &&
 	    machine_type_mismatch(file, "ARM64", NULL, 0))
 		goto err;
+	else if (STRNEQ(header->utsname.machine, "riscv64") &&
+	    machine_type_mismatch(file, "RISCV64", NULL, 0))
+		goto err;
 
 	if (header->block_size != block_size) {
 		block_size = header->block_size;
@@ -780,6 +783,8 @@ restart:
 		dd->machine_type = EM_AARCH64;
 	else if (machine_type("SPARC64"))
 		dd->machine_type = EM_SPARCV9;
+	else if (machine_type("RISCV64"))
+		dd->machine_type = EM_RISCV;
 	else {
 		error(INFO, "%s: unsupported machine type: %s\n", 
 			DISKDUMP_VALID() ? "diskdump" : "compressed kdump",
@@ -1751,7 +1756,8 @@ dump_note_offsets(FILE *fp)
 			qemu = FALSE;
 			if (machine_type("X86_64") || machine_type("S390X") ||
 			    machine_type("ARM64") || machine_type("PPC64") ||
-			    machine_type("SPARC64") || machine_type("MIPS64")) {
+			    machine_type("SPARC64") || machine_type("MIPS64") ||
+			    machine_type("RISCV64")) {
 				note64 = (void *)dd->notes_buf + tot;
 				len = sizeof(Elf64_Nhdr);
 				if (STRNEQ((char *)note64 + len, "QEMU"))
@@ -2558,7 +2564,8 @@ dump_registers_for_compressed_kdump(void)
 	if (!KDUMP_CMPRS_VALID() || (dd->header->header_version < 4) ||
 	    !(machine_type("X86") || machine_type("X86_64") ||
 	      machine_type("ARM64") || machine_type("PPC64") ||
-	      machine_type("MIPS") || machine_type("MIPS64")))
+	      machine_type("MIPS") || machine_type("MIPS64") ||
+	      machine_type("RISCV64")))
 		error(FATAL, "-r option not supported for this dumpfile\n");
 
 	if (machine_type("ARM64") && (kt->cpus != dd->num_prstatus_notes))
diff --git a/help.c b/help.c
index 99214c1..a7258d4 100644
--- a/help.c
+++ b/help.c
@@ -9512,8 +9512,8 @@ char *README[] = {
 "  These are the current prerequisites: ",
 "",
 "  o  At this point, x86, ia64, x86_64, ppc64, ppc, arm, arm64, alpha, mips,",
-"     mips64, s390 and s390x-based kernels are supported.  Other architectures",
-"     may be addressed in the future.",
+"     mips64, riscv64, s390 and s390x-based kernels are supported.  Other",
+"     architectures may be addressed in the future.",
 "",
 "  o  One size fits all -- the utility can be run on any Linux kernel version",
 "     version dating back to 2.2.5-15.  A primary design goal is to always",
@@ -9572,6 +9572,8 @@ README_ENTER_DIRECTORY,
 "     arm64 dumpfiles may be built by typing \"make target=ARM64\".",
 "  o  On an x86_64 host, an x86_64 binary that can be used to analyze",
 "     ppc64le dumpfiles may be built by typing \"make target=PPC64\".",
+"  o  On an x86_64 host, an x86_64 binary that can be used to analyze",
+"     riscv64 dumpfiles may be built by typing \"make target=RISCV64\".",
 "",
 "  Traditionally when vmcores are compressed via the makedumpfile(8) facility",
 "  the libz compression library is used, and by default the crash utility",
diff --git a/lkcd_vmdump_v1.h b/lkcd_vmdump_v1.h
index 4933427..98ee094 100644
--- a/lkcd_vmdump_v1.h
+++ b/lkcd_vmdump_v1.h
@@ -114,14 +114,8 @@ typedef struct _dump_header_s {
 	struct new_utsname   dh_utsname;
 
 	/* the dump registers */
-#ifndef IA64
-#ifndef S390
-#ifndef S390X
-#ifndef ARM64
+#if !defined(IA64) && !defined(S390) && !defined(S390X) && !defined(ARM64) && !defined(RISCV64)
 	struct pt_regs       dh_regs;
-#endif
-#endif
-#endif
 #endif
 
 	/* the address of the current task */
diff --git a/lkcd_vmdump_v2_v3.h b/lkcd_vmdump_v2_v3.h
index 984c2c2..ef3067f 100644
--- a/lkcd_vmdump_v2_v3.h
+++ b/lkcd_vmdump_v2_v3.h
@@ -37,7 +37,7 @@
 
 #if defined(ARM) || defined(X86) || defined(PPC) || defined(S390) || \
 	defined(S390X) || defined(ARM64) || defined(MIPS) || \
-	defined(MIPS64) || defined(SPARC64)
+	defined(MIPS64) || defined(SPARC64) || defined(RISCV64)
 
 /*
  * Kernel header file for Linux crash dumps.
@@ -84,13 +84,9 @@ typedef struct _dump_header_asm_s {
 	uint32_t             dha_eip;
 
 	/* the dump registers */
-#ifndef S390
-#ifndef S390X
-#ifndef ARM64
+#if !defined(S390) && !defined(S390X) && !defined(ARM64) && !defined(RISCV64)
 	struct pt_regs       dha_regs;
 #endif
-#endif
-#endif
 
 } dump_header_asm_t;
 
diff --git a/netdump.c b/netdump.c
index ff273b4..4ec12a0 100644
--- a/netdump.c
+++ b/netdump.c
@@ -300,6 +300,12 @@ is_netdump(char *file, ulong source_query)
 				goto bailout;
 			break;
 
+		case EM_RISCV:
+			if (machine_type_mismatch(file, "RISCV64", NULL,
+			    source_query))
+				goto bailout;
+			break;
+
 		default:
 			if (machine_type_mismatch(file, "(unknown)", NULL,
 			    source_query))
@@ -2935,7 +2941,8 @@ dump_registers_for_elf_dumpfiles(void)
 
         if (!(machine_type("X86") || machine_type("X86_64") || 
 	    machine_type("ARM64") || machine_type("PPC64") ||
-	    machine_type("MIPS") || machine_type("MIPS64")))
+	    machine_type("MIPS") || machine_type("MIPS64") ||
+	    machine_type("RISCV64")))
                 error(FATAL, "-r option not supported for this dumpfile\n");
 
 	if (NETDUMP_DUMPFILE()) {
diff --git a/ramdump.c b/ramdump.c
index a206fcb..d2bd7ff 100644
--- a/ramdump.c
+++ b/ramdump.c
@@ -188,6 +188,8 @@ char *ramdump_to_elf(void)
 		e_machine = EM_MIPS;
 	else if (machine_type("X86_64"))
 		e_machine = EM_X86_64;
+	else if (machine_type("RISCV64"))
+		e_machine = EM_RISCV;
 	else
 		error(FATAL, "ramdump: unsupported machine type: %s\n", 
 			MACHINE_TYPE);
diff --git a/riscv64.c b/riscv64.c
new file mode 100644
index 0000000..4f858a4
--- /dev/null
+++ b/riscv64.c
@@ -0,0 +1,54 @@
+/* riscv64.c - core analysis suite
+ *
+ * Copyright (C) 2022 Alibaba Group Holding Limited.
+ *
+ * This program is free software; you can redistribute it and/or modify
+ * it under the terms of the GNU General Public License as published by
+ * the Free Software Foundation; either version 2 of the License, or
+ * (at your option) any later version.
+ *
+ * This program is distributed in the hope that it will be useful,
+ * but WITHOUT ANY WARRANTY; without even the implied warranty of
+ * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
+ * GNU General Public License for more details.
+ */
+#include "defs.h"
+#ifdef RISCV64
+
+#include <elf.h>
+
+void
+riscv64_dump_machdep_table(ulong arg)
+{
+}
+
+/*
+ *  Include both vmalloc'd and module address space as VMALLOC space.
+ */
+int
+riscv64_IS_VMALLOC_ADDR(ulong vaddr)
+{
+	return ((vaddr >= VMALLOC_START && vaddr <= VMALLOC_END) ||
+		(vaddr >= VMEMMAP_VADDR && vaddr <= VMEMMAP_END) ||
+		(vaddr >= MODULES_VADDR && vaddr <= MODULES_END));
+}
+
+void
+riscv64_init(int when)
+{
+}
+
+void
+riscv64_display_regs_from_elf_notes(int cpu, FILE *ofp)
+{
+}
+
+#else /* !RISCV64 */
+
+void
+riscv64_display_regs_from_elf_notes(int cpu, FILE *ofp)
+{
+	return;
+}
+
+#endif /* !RISCV64 */
diff --git a/symbols.c b/symbols.c
index 42c4eb4..ebc31a2 100644
--- a/symbols.c
+++ b/symbols.c
@@ -3743,6 +3743,11 @@ is_kernel(char *file)
 				goto bailout;
 			break;
 
+		case EM_RISCV:
+			if (machine_type_mismatch(file, "RISCV64", NULL, 0))
+				goto bailout;
+			break;
+
 		default:
 			if (machine_type_mismatch(file, "(unknown)", NULL, 0))
 				goto bailout;
@@ -4002,6 +4007,11 @@ is_shared_object(char *file)
 			if (machine_type("MIPS64"))
 				return TRUE;
 			break;
+
+		case EM_RISCV:
+			if (machine_type("RISCV64"))
+				return TRUE;
+			break;
 		}
 
 		if (CRASHDEBUG(1))
-- 
2.41.0


From 3323ffc38fa913c2d58646368c5eec6e8f45bd0d Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:07 +0800
Subject: [PATCH 2/9] RISCV64: Make crash tool enter command line and support
 some commands

1. Add riscv64_init() implementation, do all necessary machine-specific setup,
   which will be called multiple times during initialization.
2. Add riscv64 sv39/48/57 pagetable macro definitions, the function of converting
   virtual address to a physical address via 4K page table.
   For 2M and 1G pagesize, they will be implemented in the future(currently not supported).
3. Add the implementation of the vtop command, which is used to convert a
   virtual address to a physical address(call the functions defined in 2).
4. Add the implementation to get virtual memory layout, va_bits, phys_ram_base
   from vmcoreinfo. As these configurations changes from time to time, we sent
   a Linux kernel patch to export these configurations, which can simplify the
   development of crash tool.
   The kernel commit: 649d6b1019a2 ("RISC-V: Add arch_crash_save_vmcoreinfo")
5. Add riscv64_get_smp_cpus() implementation, get the number of cpus.
6. Add riscv64_get_page_size() implementation, get page size.
And so on.

With this patch, we can enter crash command line, and run "vtop", "mod", "rd",
"*", "p", "kmem" ...

Tested on QEMU RISCV64 end and SoC platform of T-head Xuantie 910 CPU.

      KERNEL: vmlinux
    DUMPFILE: vmcore
        CPUS: 1
        DATE: Fri Jul 15 10:24:25 CST 2022
      UPTIME: 00:00:33
LOAD AVERAGE: 0.05, 0.01, 0.00
       TASKS: 41
    NODENAME: buildroot
     RELEASE: 5.18.9
     VERSION: #30 SMP Fri Jul 15 09:47:03 CST 2022
     MACHINE: riscv64  (unknown Mhz)
      MEMORY: 1 GB
       PANIC: "Kernel panic - not syncing: sysrq triggered crash"
         PID: 113
     COMMAND: "sh"
        TASK: ff60000002269600  [THREAD_INFO: ff60000002269600]
         CPU: 0
       STATE: TASK_RUNNING (PANIC)

crash> p mem_map
mem_map = $1 = (struct page *) 0xff6000003effbf00

crash> p /x *(struct page *) 0xff6000003effbf00
$5 = {
  flags = 0x1000,
  {
    {
      {
        lru = {
          next = 0xff6000003effbf08,
          prev = 0xff6000003effbf08
        },
        {
          __filler = 0xff6000003effbf08,
          mlock_count = 0x3effbf08
        }
      },
      mapping = 0x0,
      index = 0x0,
      private = 0x0
    },

crash> mod
     MODULE       NAME             BASE         SIZE  OBJECT FILE
ffffffff0113e740  nvme_core  ffffffff01133000  98304  (not loaded)  [CONFIG_KALLSYMS]
ffffffff011542c0  nvme       ffffffff0114c000  61440  (not loaded)  [CONFIG_KALLSYMS]

crash> rd ffffffff0113e740 8
ffffffff0113e740:  0000000000000000 ffffffff810874f8   .........t......
ffffffff0113e750:  ffffffff011542c8 726f635f656d766e   .B......nvme_cor
ffffffff0113e760:  0000000000000065 0000000000000000   e...............
ffffffff0113e770:  0000000000000000 0000000000000000   ................

crash> vtop ffffffff0113e740
VIRTUAL           PHYSICAL
ffffffff0113e740  8254d740

  PGD: ffffffff810e9ff8 => 2ffff001
  P4D: 0000000000000000 => 000000002fffec01
  PUD: 00005605c2957470 => 0000000020949801
  PMD: 00007fff7f1750c0 => 0000000020947401
  PTE: 0 => 209534e7
 PAGE: 000000008254d000

  PTE     PHYSICAL  FLAGS
209534e7  8254d000  (PRESENT|READ|WRITE|GLOBAL|ACCESSED|DIRTY)

      PAGE       PHYSICAL      MAPPING       INDEX CNT FLAGS
ff6000003f0777d8 8254d000                0        0  1 0

Tested-by: Yixun Lan <yixun.lan@gmail.com>
Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 defs.h     |  97 ++++++
 diskdump.c |  10 +
 riscv64.c  | 994 +++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 1101 insertions(+)

diff --git a/defs.h b/defs.h
index d715378..b65162e 100644
--- a/defs.h
+++ b/defs.h
@@ -3494,6 +3494,85 @@ struct arm64_stackframe {
 #define _64BIT_
 #define MACHINE_TYPE		"RISCV64"
 
+typedef struct { ulong pgd; } pgd_t;
+typedef struct { ulong p4d; } p4d_t;
+typedef struct { ulong pud; } pud_t;
+typedef struct { ulong pmd; } pmd_t;
+typedef struct { ulong pte; } pte_t;
+typedef signed int s32;
+
+/* arch/riscv/include/asm/pgtable-64.h */
+#define PGD_SHIFT_L3		(30)
+#define PGD_SHIFT_L4		(39)
+#define PGD_SHIFT_L5		(48)
+
+#define P4D_SHIFT		(39)
+#define PUD_SHIFT		(30)
+#define PMD_SHIFT		(21)
+
+#define PTRS_PER_PGD		(512)
+#define PTRS_PER_P4D		(512)
+#define PTRS_PER_PUD		(512)
+#define PTRS_PER_PMD		(512)
+#define PTRS_PER_PTE		(512)
+
+/*
+ * Mask for bit 0~53(PROT and PPN) of PTE
+ * 63 6261  60    54  53 10  9 8 7 6 5 4 3 2 1 0
+ * N  PBMT  Reserved  P P N  RSW D A G U X W R V
+ */
+#define PTE_PFN_PROT_MASK	0x3FFFFFFFFFFFFF
+
+/*
+ * 3-levels / 4K pages
+ *
+ * sv39
+ * PGD  |  PMD  |  PTE  |  OFFSET  |
+ *  9   |   9   |   9   |    12    |
+ */
+#define pgd_index_l3_4k(addr) (((addr) >> PGD_SHIFT_L3) & (PTRS_PER_PGD - 1))
+#define pmd_index_l3_4k(addr) (((addr) >> PMD_SHIFT) & (PTRS_PER_PMD - 1))
+#define pte_index_l3_4k(addr) (((addr) >> PAGESHIFT()) & (PTRS_PER_PTE - 1))
+
+/*
+ * 4-levels / 4K pages
+ *
+ * sv48
+ * PGD  |  PUD  |  PMD  |   PTE   |  OFFSET  |
+ *  9   |   9   |   9   |    9    |    12    |
+ */
+#define pgd_index_l4_4k(addr) (((addr) >> PGD_SHIFT_L4) & (PTRS_PER_PGD - 1))
+#define pud_index_l4_4k(addr) (((addr) >> PUD_SHIFT) & (PTRS_PER_PUD - 1))
+#define pmd_index_l4_4k(addr) (((addr) >> PMD_SHIFT) & (PTRS_PER_PMD - 1))
+#define pte_index_l4_4k(addr) (((addr) >> PAGESHIFT()) & (PTRS_PER_PTE - 1))
+
+/*
+ * 5-levels / 4K pages
+ *
+ * sv57
+ * PGD  |  P4D  |  PUD  |  PMD  |   PTE   |  OFFSET  |
+ *  9   |   9   |   9   |   9   |    9    |    12    |
+ */
+#define pgd_index_l5_4k(addr) (((addr) >> PGD_SHIFT_L5) & (PTRS_PER_PGD - 1))
+#define p4d_index_l5_4k(addr) (((addr) >> P4D_SHIFT) & (PTRS_PER_P4D - 1))
+#define pud_index_l5_4k(addr) (((addr) >> PUD_SHIFT) & (PTRS_PER_PUD - 1))
+#define pmd_index_l5_4k(addr) (((addr) >> PMD_SHIFT) & (PTRS_PER_PMD - 1))
+#define pte_index_l5_4k(addr) (((addr) >> PAGESHIFT()) & (PTRS_PER_PTE - 1))
+
+#define VM_L3_4K	(0x2)
+#define VM_L3_2M	(0x4)
+#define VM_L3_1G	(0x8)
+#define VM_L4_4K	(0x10)
+#define VM_L4_2M	(0x20)
+#define VM_L4_1G	(0x40)
+#define VM_L5_4K	(0x80)
+#define VM_L5_2M	(0x100)
+#define VM_L5_1G	(0x200)
+
+#define VM_FLAGS	(VM_L3_4K | VM_L3_2M | VM_L3_1G | \
+			 VM_L4_4K | VM_L4_2M | VM_L4_1G | \
+			 VM_L5_4K | VM_L5_2M | VM_L5_1G)
+
 /*
  * Direct memory mapping
  */
@@ -3545,6 +3624,14 @@ struct arm64_stackframe {
 #define PHYS_MASK_SHIFT 	_MAX_PHYSMEM_BITS
 #define PHYS_MASK		(((1UL) << PHYS_MASK_SHIFT) - 1)
 
+#define IS_LAST_P4D_READ(p4d)	((ulong)(p4d) == machdep->machspec->last_p4d_read)
+#define FILL_P4D(P4D, TYPE, SIZE)					      \
+    if (!IS_LAST_P4D_READ(P4D)) {					      \
+	    readmem((ulonglong)((ulong)(P4D)), TYPE, machdep->machspec->p4d,  \
+		     SIZE, "p4d page", FAULT_ON_ERROR);                       \
+	    machdep->machspec->last_p4d_read = (ulong)(P4D);                  \
+    }
+
 #endif  /* RISCV64 */
 
 #ifdef X86
@@ -6811,6 +6898,10 @@ struct machine_specific {
 	ulong _page_soft;
 
 	ulong _pfn_shift;
+	ulong va_bits;
+	char *p4d;
+	ulong last_p4d_read;
+	ulong struct_page_size;
 
 	struct riscv64_register *crash_task_regs;
 };
@@ -6834,6 +6925,12 @@ struct machine_specific {
 #define _PAGE_PROT_NONE _PAGE_READ
 #define _PAGE_PFN_SHIFT 10
 
+/* from 'struct pt_regs' definitions of RISC-V arch */
+#define RISCV64_REGS_EPC  0
+#define RISCV64_REGS_RA   1
+#define RISCV64_REGS_SP   2
+#define RISCV64_REGS_FP   8
+
 #endif /* RISCV64 */
 
 /*
diff --git a/diskdump.c b/diskdump.c
index 28503bc..cf5f5d9 100644
--- a/diskdump.c
+++ b/diskdump.c
@@ -1531,6 +1531,12 @@ get_diskdump_regs_mips(struct bt_info *bt, ulong *eip, ulong *esp)
 	machdep->get_stack_frame(bt, eip, esp);
 }
 
+static void
+get_diskdump_regs_riscv64(struct bt_info *bt, ulong *eip, ulong *esp)
+{
+	machdep->get_stack_frame(bt, eip, esp);
+}
+
 static void
 get_diskdump_regs_sparc64(struct bt_info *bt, ulong *eip, ulong *esp)
 {
@@ -1610,6 +1616,10 @@ get_diskdump_regs(struct bt_info *bt, ulong *eip, ulong *esp)
 		get_diskdump_regs_sparc64(bt, eip, esp);
 		break;
 
+	case EM_RISCV:
+		get_diskdump_regs_riscv64(bt, eip, esp);
+		break;
+
 	default:
 		error(FATAL, "%s: unsupported machine type: %s\n",
 			DISKDUMP_VALID() ? "diskdump" : "compressed kdump",
diff --git a/riscv64.c b/riscv64.c
index 4f858a4..d8de3d5 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -16,10 +16,314 @@
 #ifdef RISCV64
 
 #include <elf.h>
+#include <math.h>
+
+static ulong riscv64_get_page_size(void);
+static int riscv64_vtop_3level_4k(ulong *pgd, ulong vaddr,
+				   physaddr_t *paddr, int verbose);
+static int riscv64_vtop_4level_4k(ulong *pgd, ulong vaddr,
+				   physaddr_t *paddr, int verbose);
+static int riscv64_vtop_5level_4k(ulong *pgd, ulong vaddr,
+				   physaddr_t *paddr, int verbose);
+static void riscv64_page_type_init(void);
+static int riscv64_is_kvaddr(ulong vaddr);
+static int riscv64_is_uvaddr(ulong vaddr, struct task_context *tc);
+static int riscv64_uvtop(struct task_context *tc, ulong vaddr,
+			  physaddr_t *paddr, int verbose);
+static int riscv64_kvtop(struct task_context *tc, ulong kvaddr,
+			  physaddr_t *paddr, int verbose);
+static void riscv64_cmd_mach(void);
+static int riscv64_translate_pte(ulong, void *, ulonglong);
+static int riscv64_init_active_task_regs(void);
+static int riscv64_get_crash_notes(void);
+static int riscv64_get_elf_notes(void);
+static void riscv64_get_va_range(struct machine_specific *ms);
+static void riscv64_get_va_bits(struct machine_specific *ms);
+static void riscv64_get_struct_page_size(struct machine_specific *ms);
+
+#define REG_FMT 	"%016lx"
+#define SZ_2G		0x80000000
+
+/*
+ * Holds registers during the crash.
+ */
+static struct riscv64_register *panic_task_regs;
+
+/* from arch/riscv/include/asm/stacktrace.h */
+struct stackframe {
+	ulong fp;
+	ulong ra;
+};
+
+static struct machine_specific riscv64_machine_specific = {
+	._page_present = (1 << 0),
+	._page_read = (1 << 1),
+	._page_write = (1 << 2),
+	._page_exec = (1 << 3),
+	._page_user = (1 << 4),
+	._page_global = (1 << 5),
+	._page_accessed = (1 << 6),
+	._page_dirty = (1 << 7),
+	._page_soft = (1 << 8),
+
+	.va_bits = 0,
+	.struct_page_size = 0,
+};
+
+static void
+pt_level_alloc(char **lvl, char *name)
+{
+	size_t sz = PAGESIZE();
+	void *pointer = malloc(sz);
+
+	if (!pointer)
+		error(FATAL, name);
+	*lvl = pointer;
+}
+
+static ulong
+riscv64_get_page_size(void)
+{
+	return memory_page_size();
+}
+
+static ulong
+riscv64_vmalloc_start(void)
+{
+	return ((ulong)VMALLOC_START);
+}
+
+/* Get the size of struct page {} */
+static void riscv64_get_struct_page_size(struct machine_specific *ms)
+{
+	char *string;
+
+	string = pc->read_vmcoreinfo("SIZE(page)");
+	if (string) {
+		ms->struct_page_size = atol(string);
+		free(string);
+	}
+}
+
+static void
+riscv64_cmd_mach(void)
+{
+	/* TODO: */
+}
+
+static int
+riscv64_verify_symbol(const char *name, ulong value, char type)
+{
+	/* TODO: */
+	return TRUE;
+}
 
 void
 riscv64_dump_machdep_table(ulong arg)
 {
+	/* TODO: */
+}
+
+static ulong
+riscv64_processor_speed(void)
+{
+	/* TODO: */
+	return 0;
+}
+
+static unsigned long riscv64_get_kernel_version(void)
+{
+	char *string;
+	char buf[BUFSIZE];
+	char *p1, *p2;
+
+	if (THIS_KERNEL_VERSION)
+		return THIS_KERNEL_VERSION;
+
+	string = pc->read_vmcoreinfo("OSRELEASE");
+	if (string) {
+		strcpy(buf, string);
+
+		p1 = p2 = buf;
+		while (*p2 != '.')
+			p2++;
+		*p2 = NULLCHAR;
+		kt->kernel_version[0] = atoi(p1);
+
+		p1 = ++p2;
+		while (*p2 != '.')
+			p2++;
+		*p2 = NULLCHAR;
+		kt->kernel_version[1] = atoi(p1);
+
+		p1 = ++p2;
+		while ((*p2 >= '0') && (*p2 <= '9'))
+			p2++;
+		*p2 = NULLCHAR;
+		kt->kernel_version[2] = atoi(p1);
+		free(string);
+	}
+	return THIS_KERNEL_VERSION;
+}
+
+static void
+riscv64_get_phys_ram_base(struct machine_specific *ms)
+{
+	unsigned long kernel_version = riscv64_get_kernel_version();
+
+	/*
+	 * phys_ram_base is defined in Linux kernel since 5.14.
+	 */
+	if (kernel_version >= LINUX(5,14,0)) {
+		char *string;
+		if ((string = pc->read_vmcoreinfo("NUMBER(phys_ram_base)"))) {
+			ms->phys_base = atol(string);
+			free(string);
+		} else
+			error(FATAL, "cannot read phys_ram_base\n");
+	} else
+		/*
+		 * For qemu rv64 env and hardware platform, default phys base
+		 * may different, eg,
+		 *	hardware platform: 0x200000
+		 *	qemu   rv64   env: 0x80200000
+		 *
+		 * But we only can set one default value, in this case, qemu
+		 * rv64 env may can't work.
+		 */
+		ms->phys_base = 0x200000;
+}
+
+static void riscv64_get_va_bits(struct machine_specific *ms)
+{
+	unsigned long kernel_version = riscv64_get_kernel_version();
+
+	/*
+	 * VA_BITS is defined in Linux kernel since 5.17. So we use the
+	 * default va bits 39 when Linux version < 5.17.
+	 */
+	if (kernel_version >= LINUX(5,17,0)) {
+		char *string;
+		if ((string = pc->read_vmcoreinfo("NUMBER(VA_BITS)"))) {
+			ms->va_bits = atol(string);
+			free(string);
+		}
+	} else
+		ms->va_bits = 39;
+}
+
+static void riscv64_get_va_range(struct machine_specific *ms)
+{
+	unsigned long kernel_version = riscv64_get_kernel_version();
+	char *string;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(PAGE_OFFSET)"))) {
+		ms->page_offset = htol(string, QUIET, NULL);
+		free(string);
+	} else
+		goto error;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(VMALLOC_START)"))) {
+		ms->vmalloc_start_addr = htol(string, QUIET, NULL);
+		free(string);
+	} else
+		goto error;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(VMALLOC_END)"))) {
+		ms->vmalloc_end = htol(string, QUIET, NULL);
+                free(string);
+	} else
+		goto error;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(VMEMMAP_START)"))) {
+		ms->vmemmap_vaddr = htol(string, QUIET, NULL);
+		free(string);
+	} else
+		goto error;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(VMEMMAP_END)"))) {
+		ms->vmemmap_end = htol(string, QUIET, NULL);
+		free(string);
+	} else
+		goto error;
+
+	if ((string = pc->read_vmcoreinfo("NUMBER(KERNEL_LINK_ADDR)"))) {
+		ms->kernel_link_addr = htol(string, QUIET, NULL);
+		free(string);
+	} else
+		goto error;
+
+	/*
+	 * From Linux 5.13, the kernel mapping is moved to the last 2GB
+	 * of the address space, modules use the 2GB memory range right
+	 * before the kernel. Before Linux 5.13, modules area is embedded
+	 * in vmalloc area.
+	 *
+	 */
+	if (kernel_version >= LINUX(5,13,0)) {
+		if ((string = pc->read_vmcoreinfo("NUMBER(MODULES_VADDR)"))) {
+			ms->modules_vaddr = htol(string, QUIET, NULL);
+			free(string);
+		} else
+			goto error;
+
+		if ((string = pc->read_vmcoreinfo("NUMBER(MODULES_END)"))) {
+			ms->modules_end = htol(string, QUIET, NULL);
+			free(string);
+		} else
+			goto error;
+	} else {
+		ms->modules_vaddr = ms->vmalloc_start_addr;
+		ms->modules_end = ms->vmalloc_end;
+	}
+
+	if (CRASHDEBUG(1)) {
+		fprintf(fp, "vmemmap	: 0x%lx - 0x%lx\n",
+			ms->vmemmap_vaddr, ms->vmemmap_end);
+		fprintf(fp, "vmalloc	: 0x%lx - 0x%lx\n",
+			ms->vmalloc_start_addr, ms->vmalloc_end);
+		fprintf(fp, "mudules	: 0x%lx - 0x%lx\n",
+			ms->modules_vaddr, ms->modules_end);
+		fprintf(fp, "lowmem	: 0x%lx -\n", ms->page_offset);
+		fprintf(fp, "kernel link addr	: 0x%lx\n",
+			ms->kernel_link_addr);
+	}
+	return;
+error:
+	error(FATAL, "cannot get vm layout\n");
+}
+
+static int
+riscv64_is_kvaddr(ulong vaddr)
+{
+	if (IS_VMALLOC_ADDR(vaddr))
+		return TRUE;
+
+	return (vaddr >= machdep->kvbase);
+}
+
+static int
+riscv64_is_uvaddr(ulong vaddr, struct task_context *unused)
+{
+	if (IS_VMALLOC_ADDR(vaddr))
+		return FALSE;
+
+	return (vaddr < machdep->kvbase);
+}
+
+static int
+riscv64_is_task_addr(ulong task)
+{
+	if (tt->flags & THREAD_INFO)
+		return IS_KVADDR(task);
+
+	return (IS_KVADDR(task) && ALIGNED_STACK_OFFSET(task) == 0);
+}
+
+static int
+riscv64_get_smp_cpus(void)
+{
+	return (get_cpus_present() > 0) ? get_cpus_present() : kt->cpus;
 }
 
 /*
@@ -33,11 +337,701 @@ riscv64_IS_VMALLOC_ADDR(ulong vaddr)
 		(vaddr >= MODULES_VADDR && vaddr <= MODULES_END));
 }
 
+/*
+ * Translate a PTE, returning TRUE if the page is present.
+ * If a physaddr pointer is passed in, don't print anything.
+ */
+static int
+riscv64_translate_pte(ulong pte, void *physaddr, ulonglong unused)
+{
+	char ptebuf[BUFSIZE];
+	char physbuf[BUFSIZE];
+	char buf[BUFSIZE];
+	int page_present;
+	int len1, len2, others;
+	ulong paddr;
+
+	paddr = PTOB(pte >> _PAGE_PFN_SHIFT);
+	page_present = !!(pte & _PAGE_PRESENT);
+
+	if (physaddr) {
+		*(ulong *)physaddr = paddr;
+		return page_present;
+	}
+
+	sprintf(ptebuf, "%lx", pte);
+	len1 = MAX(strlen(ptebuf), strlen("PTE"));
+	fprintf(fp, "%s  ", mkstring(buf, len1, CENTER | LJUST, "PTE"));
+
+	if (!page_present)
+		return page_present;
+
+	sprintf(physbuf, "%lx", paddr);
+	len2 = MAX(strlen(physbuf), strlen("PHYSICAL"));
+	fprintf(fp, "%s  ", mkstring(buf, len2, CENTER | LJUST, "PHYSICAL"));
+
+	fprintf(fp, "FLAGS\n");
+	fprintf(fp, "%s  %s  ",
+		mkstring(ptebuf, len1, CENTER | RJUST, NULL),
+		mkstring(physbuf, len2, CENTER | RJUST, NULL));
+
+	fprintf(fp, "(");
+	others = 0;
+
+#define CHECK_PAGE_FLAG(flag)				\
+	if ((_PAGE_##flag) && (pte & _PAGE_##flag))	\
+		fprintf(fp, "%s" #flag, others++ ? "|" : "")
+	if (pte) {
+		CHECK_PAGE_FLAG(PRESENT);
+		CHECK_PAGE_FLAG(READ);
+		CHECK_PAGE_FLAG(WRITE);
+		CHECK_PAGE_FLAG(EXEC);
+		CHECK_PAGE_FLAG(USER);
+		CHECK_PAGE_FLAG(GLOBAL);
+		CHECK_PAGE_FLAG(ACCESSED);
+		CHECK_PAGE_FLAG(DIRTY);
+		CHECK_PAGE_FLAG(SOFT);
+	} else {
+		fprintf(fp, "no mapping");
+	}
+
+	fprintf(fp, ")\n");
+
+	return page_present;
+}
+
+static void
+riscv64_page_type_init(void)
+{
+	ulong va_bits = machdep->machspec->va_bits;
+
+	/*
+	 * For RISCV64 arch, any level of PTE may be a leaf PTE,
+	 * so in addition to 4KiB pages,
+	 * Sv39 supports 2 MiB megapages, 1 GiB gigapages;
+	 * Sv48 supports 2 MiB megapages, 1 GiB gigapages, 512 GiB terapages;
+	 * Sv57 supports 2 MiB megapages, 1 GiB gigapages, 512 GiB terapages, and 256 TiB petapages.
+	 *
+	 * refs to riscv-privileged spec.
+	 *
+	 * We just support 4KiB, 2MiB, 1GiB now.
+	 */
+	switch (machdep->pagesize)
+	{
+	case 0x1000:		// 4 KiB
+		machdep->flags |= (va_bits == 57 ? VM_L5_4K :
+				  (va_bits == 48 ? VM_L4_4K : VM_L3_4K));
+		break;
+	case 0x200000:		// 2 MiB
+		/* TODO: */
+	case 0x40000000: 	// 1 GiB
+		/* TODO: */
+	default:
+		if (machdep->pagesize)
+			error(FATAL, "invalid/unsupported page size: %d\n",
+			      machdep->pagesize);
+		else
+			error(FATAL, "cannot determine page size\n");
+	}
+}
+
+static int
+riscv64_vtop_3level_4k(ulong *pgd, ulong vaddr, physaddr_t *paddr, int verbose)
+{
+	ulong *pgd_ptr, pgd_val;
+	ulong pmd_val;
+	ulong pte_val, pte_pfn;
+	ulong pt_phys;
+
+	/* PGD */
+	pgd_ptr = pgd + pgd_index_l3_4k(vaddr);
+	FILL_PGD(pgd, KVADDR, PAGESIZE());
+	pgd_val = ULONG(machdep->pgd + PAGEOFFSET(pgd_ptr));
+	if (verbose)
+		fprintf(fp, "  PGD: %lx => %lx\n", (ulong)pgd_ptr, pgd_val);
+	if (!pgd_val)
+		goto no_page;
+	pgd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pgd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PMD */
+	FILL_PMD(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pmd_val = ULONG(machdep->pmd + PAGEOFFSET(sizeof(pmd_t) *
+			pmd_index_l3_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PMD: %016lx => %016lx\n", pt_phys, pmd_val);
+	if (!pmd_val)
+		goto no_page;
+	pmd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pmd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PTE */
+	FILL_PTBL(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pte_val = ULONG(machdep->ptbl + PAGEOFFSET(sizeof(pte_t) *
+			pte_index_l3_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PTE: %lx => %lx\n", pt_phys, pte_val);
+	if (!pte_val)
+		goto no_page;
+	pte_val &= PTE_PFN_PROT_MASK;
+	pte_pfn = pte_val >> _PAGE_PFN_SHIFT;
+
+	if (!(pte_val & _PAGE_PRESENT)) {
+		if (verbose) {
+			fprintf(fp, "\n");
+			riscv64_translate_pte((ulong)pte_val, 0, 0);
+		}
+		fprintf(fp, " PAGE: %016lx not present\n\n", PAGEBASE(*paddr));
+		return FALSE;
+	}
+
+	*paddr = PTOB(pte_pfn) + PAGEOFFSET(vaddr);
+
+	if (verbose) {
+		fprintf(fp, " PAGE: %016lx\n\n", PAGEBASE(*paddr));
+		riscv64_translate_pte(pte_val, 0, 0);
+	}
+
+	return TRUE;
+no_page:
+	fprintf(fp, "invalid\n");
+	return FALSE;
+}
+
+static int
+riscv64_vtop_4level_4k(ulong *pgd, ulong vaddr, physaddr_t *paddr, int verbose)
+{
+	ulong *pgd_ptr, pgd_val;
+	ulong pud_val;
+	ulong pmd_val;
+	ulong pte_val, pte_pfn;
+	ulong pt_phys;
+
+	/* PGD */
+	pgd_ptr = pgd + pgd_index_l4_4k(vaddr);
+	FILL_PGD(pgd, KVADDR, PAGESIZE());
+	pgd_val = ULONG(machdep->pgd + PAGEOFFSET(pgd_ptr));
+	if (verbose)
+		fprintf(fp, "  PGD: %lx => %lx\n", (ulong)pgd_ptr, pgd_val);
+	if (!pgd_val)
+		goto no_page;
+	pgd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pgd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PUD */
+	FILL_PUD(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pud_val = ULONG(machdep->pud + PAGEOFFSET(sizeof(pud_t) *
+			pud_index_l4_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PUD: %016lx => %016lx\n", pt_phys, pud_val);
+	if (!pud_val)
+		goto no_page;
+	pud_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pud_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PMD */
+	FILL_PMD(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pmd_val = ULONG(machdep->pmd + PAGEOFFSET(sizeof(pmd_t) *
+			pmd_index_l4_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PMD: %016lx => %016lx\n", pt_phys, pmd_val);
+	if (!pmd_val)
+		goto no_page;
+	pmd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pmd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PTE */
+	FILL_PTBL(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pte_val = ULONG(machdep->ptbl + PAGEOFFSET(sizeof(pte_t) *
+			pte_index_l4_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PTE: %lx => %lx\n", pt_phys, pte_val);
+	if (!pte_val)
+		goto no_page;
+	pte_val &= PTE_PFN_PROT_MASK;
+	pte_pfn = pte_val >> _PAGE_PFN_SHIFT;
+
+	if (!(pte_val & _PAGE_PRESENT)) {
+		if (verbose) {
+			fprintf(fp, "\n");
+			riscv64_translate_pte((ulong)pte_val, 0, 0);
+		}
+		fprintf(fp, " PAGE: %016lx not present\n\n", PAGEBASE(*paddr));
+		return FALSE;
+	}
+
+	*paddr = PTOB(pte_pfn) + PAGEOFFSET(vaddr);
+
+	if (verbose) {
+		fprintf(fp, " PAGE: %016lx\n\n", PAGEBASE(*paddr));
+		riscv64_translate_pte(pte_val, 0, 0);
+	}
+
+	return TRUE;
+no_page:
+	fprintf(fp, "invalid\n");
+	return FALSE;
+}
+
+static int
+riscv64_vtop_5level_4k(ulong *pgd, ulong vaddr, physaddr_t *paddr, int verbose)
+{
+	ulong *pgd_ptr, pgd_val;
+	ulong p4d_val;
+	ulong pud_val;
+	ulong pmd_val;
+	ulong pte_val, pte_pfn;
+	ulong pt_phys;
+
+	/* PGD */
+	pgd_ptr = pgd + pgd_index_l5_4k(vaddr);
+	FILL_PGD(pgd, KVADDR, PAGESIZE());
+	pgd_val = ULONG(machdep->pgd + PAGEOFFSET(pgd_ptr));
+	if (verbose)
+		fprintf(fp, "  PGD: %lx => %lx\n", (ulong)pgd_ptr, pgd_val);
+	if (!pgd_val)
+		goto no_page;
+	pgd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pgd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* P4D */
+	FILL_P4D(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	p4d_val = ULONG(machdep->machspec->p4d + PAGEOFFSET(sizeof(p4d_t) *
+			p4d_index_l5_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  P4D: %016lx => %016lx\n", pt_phys, p4d_val);
+	if (!p4d_val)
+		goto no_page;
+	p4d_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (p4d_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PUD */
+	FILL_PUD(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pud_val = ULONG(machdep->pud + PAGEOFFSET(sizeof(pud_t) *
+			pud_index_l5_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PUD: %016lx => %016lx\n", pt_phys, pud_val);
+	if (!pud_val)
+		goto no_page;
+	pud_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pud_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PMD */
+	FILL_PMD(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pmd_val = ULONG(machdep->pmd + PAGEOFFSET(sizeof(pmd_t) *
+			pmd_index_l4_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PMD: %016lx => %016lx\n", pt_phys, pmd_val);
+	if (!pmd_val)
+		goto no_page;
+	pmd_val &= PTE_PFN_PROT_MASK;
+	pt_phys = (pmd_val >> _PAGE_PFN_SHIFT) << PAGESHIFT();
+
+	/* PTE */
+	FILL_PTBL(PAGEBASE(pt_phys), PHYSADDR, PAGESIZE());
+	pte_val = ULONG(machdep->ptbl + PAGEOFFSET(sizeof(pte_t) *
+			pte_index_l4_4k(vaddr)));
+	if (verbose)
+		fprintf(fp, "  PTE: %lx => %lx\n", pt_phys, pte_val);
+	if (!pte_val)
+		goto no_page;
+	pte_val &= PTE_PFN_PROT_MASK;
+	pte_pfn = pte_val >> _PAGE_PFN_SHIFT;
+
+	if (!(pte_val & _PAGE_PRESENT)) {
+		if (verbose) {
+			fprintf(fp, "\n");
+			riscv64_translate_pte((ulong)pte_val, 0, 0);
+		}
+		printf("!_PAGE_PRESENT\n");
+		return FALSE;
+	}
+
+	*paddr = PTOB(pte_pfn) + PAGEOFFSET(vaddr);
+
+	if (verbose) {
+		fprintf(fp, " PAGE: %016lx\n\n", PAGEBASE(*paddr));
+		riscv64_translate_pte(pte_val, 0, 0);
+	}
+
+	return TRUE;
+no_page:
+	fprintf(fp, "invalid\n");
+	return FALSE;
+}
+
+static int
+riscv64_init_active_task_regs(void)
+{
+	int retval;
+
+	retval = riscv64_get_crash_notes();
+	if (retval == TRUE)
+		return retval;
+
+	return riscv64_get_elf_notes();
+}
+
+/*
+ * Retrieve task registers for the time of the crash.
+ */
+static int
+riscv64_get_crash_notes(void)
+{
+	struct machine_specific *ms = machdep->machspec;
+	ulong crash_notes;
+	Elf64_Nhdr *note;
+	ulong offset;
+	char *buf, *p;
+	ulong *notes_ptrs;
+	ulong i;
+
+	/*
+	 * crash_notes contains per cpu memory for storing cpu states
+	 * in case of system crash.
+	 */
+	if (!symbol_exists("crash_notes"))
+		return FALSE;
+
+	crash_notes = symbol_value("crash_notes");
+
+	notes_ptrs = (ulong *)GETBUF(kt->cpus*sizeof(notes_ptrs[0]));
+
+	/*
+	 * Read crash_notes for the first CPU. crash_notes are in standard ELF
+	 * note format.
+	 */
+	if (!readmem(crash_notes, KVADDR, &notes_ptrs[kt->cpus-1],
+	    sizeof(notes_ptrs[kt->cpus-1]), "crash_notes",
+		     RETURN_ON_ERROR)) {
+		error(WARNING, "cannot read crash_notes\n");
+		FREEBUF(notes_ptrs);
+		return FALSE;
+	}
+
+	if (symbol_exists("__per_cpu_offset")) {
+
+		/*
+		 * Add __per_cpu_offset for each cpu to form the pointer to the notes
+		 */
+		for (i = 0; i < kt->cpus; i++)
+			notes_ptrs[i] = notes_ptrs[kt->cpus-1] + kt->__per_cpu_offset[i];
+	}
+
+	buf = GETBUF(SIZE(note_buf));
+
+	if (!(panic_task_regs = calloc((size_t)kt->cpus, sizeof(*panic_task_regs))))
+		error(FATAL, "cannot calloc panic_task_regs space\n");
+
+	for (i = 0; i < kt->cpus; i++) {
+
+		if (!readmem(notes_ptrs[i], KVADDR, buf, SIZE(note_buf), "note_buf_t",
+			     RETURN_ON_ERROR)) {
+			error(WARNING,
+				"cannot find NT_PRSTATUS note for cpu: %d\n", i);
+			goto fail;
+		}
+
+		/*
+		 * Do some sanity checks for this note before reading registers from it.
+		 */
+		note = (Elf64_Nhdr *)buf;
+		p = buf + sizeof(Elf64_Nhdr);
+
+		/*
+		 * dumpfiles created with qemu won't have crash_notes, but there will
+		 * be elf notes; dumpfiles created by kdump do not create notes for
+		 * offline cpus.
+		 */
+		if (note->n_namesz == 0 && (DISKDUMP_DUMPFILE() || KDUMP_DUMPFILE())) {
+			if (DISKDUMP_DUMPFILE())
+				note = diskdump_get_prstatus_percpu(i);
+			else if (KDUMP_DUMPFILE())
+				note = netdump_get_prstatus_percpu(i);
+			if (note) {
+				/*
+				 * SIZE(note_buf) accounts for a "final note", which is a
+				 * trailing empty elf note header.
+				 */
+				long notesz = SIZE(note_buf) - sizeof(Elf64_Nhdr);
+
+				if (sizeof(Elf64_Nhdr) + roundup(note->n_namesz, 4) +
+				    note->n_descsz == notesz)
+					BCOPY((char *)note, buf, notesz);
+			} else {
+				error(WARNING,
+					"cannot find NT_PRSTATUS note for cpu: %d\n", i);
+				continue;
+			}
+		}
+
+		/*
+		 * Check the sanity of NT_PRSTATUS note only for each online cpu.
+		 */
+		if (note->n_type != NT_PRSTATUS) {
+			error(WARNING, "invalid NT_PRSTATUS note (n_type != NT_PRSTATUS)\n");
+			goto fail;
+		}
+		if (!STRNEQ(p, "CORE")) {
+			error(WARNING, "invalid NT_PRSTATUS note (name != \"CORE\"\n");
+			goto fail;
+		}
+
+		/*
+		 * Find correct location of note data. This contains elf_prstatus
+		 * structure which has registers etc. for the crashed task.
+		 */
+		offset = sizeof(Elf64_Nhdr);
+		offset = roundup(offset + note->n_namesz, 4);
+		p = buf + offset; /* start of elf_prstatus */
+
+		BCOPY(p + OFFSET(elf_prstatus_pr_reg), &panic_task_regs[i],
+		      sizeof(panic_task_regs[i]));
+	}
+
+	/*
+	 * And finally we have the registers for the crashed task. This is
+	 * used later on when dumping backtrace.
+	 */
+	ms->crash_task_regs = panic_task_regs;
+
+	FREEBUF(buf);
+	FREEBUF(notes_ptrs);
+	return TRUE;
+
+fail:
+	FREEBUF(buf);
+	FREEBUF(notes_ptrs);
+	free(panic_task_regs);
+	return FALSE;
+}
+
+static int
+riscv64_get_elf_notes(void)
+{
+	struct machine_specific *ms = machdep->machspec;
+	int i;
+
+	if (!DISKDUMP_DUMPFILE() && !KDUMP_DUMPFILE())
+		return FALSE;
+
+	panic_task_regs = calloc(kt->cpus, sizeof(*panic_task_regs));
+	if (!panic_task_regs)
+		error(FATAL, "cannot calloc panic_task_regs space\n");
+
+	for (i = 0; i < kt->cpus; i++) {
+		Elf64_Nhdr *note = NULL;
+		size_t len;
+
+		if (DISKDUMP_DUMPFILE())
+			note = diskdump_get_prstatus_percpu(i);
+		else if (KDUMP_DUMPFILE())
+			note = netdump_get_prstatus_percpu(i);
+
+		if (!note) {
+			error(WARNING,
+				"cannot find NT_PRSTATUS note for cpu: %d\n", i);
+			continue;
+		}
+
+		len = sizeof(Elf64_Nhdr);
+		len = roundup(len + note->n_namesz, 4);
+
+		BCOPY((char *)note + len + OFFSET(elf_prstatus_pr_reg),
+		      &panic_task_regs[i], sizeof(panic_task_regs[i]));
+	}
+
+	ms->crash_task_regs = panic_task_regs;
+
+	return TRUE;
+}
+
+/*
+ * Translates a user virtual address to its physical address.
+ */
+static int
+riscv64_uvtop(struct task_context *tc, ulong uvaddr, physaddr_t *paddr, int verbose)
+{
+	ulong mm, active_mm;
+	ulong *pgd;
+
+	if (!tc)
+		error(FATAL, "current context invalid\n");
+
+	*paddr = 0;
+
+	if (is_kernel_thread(tc->task) && IS_KVADDR(uvaddr)) {
+		readmem(tc->task + OFFSET(task_struct_active_mm),
+			KVADDR, &active_mm, sizeof(void *),
+			"task active_mm contents", FAULT_ON_ERROR);
+
+		if (!active_mm)
+			error(FATAL,
+			      "no active_mm for this kernel thread\n");
+
+		readmem(active_mm + OFFSET(mm_struct_pgd),
+			KVADDR, &pgd, sizeof(long),
+			"mm_struct pgd", FAULT_ON_ERROR);
+	} else {
+		if ((mm = task_mm(tc->task, TRUE)))
+			pgd = ULONG_PTR(tt->mm_struct + OFFSET(mm_struct_pgd));
+		else
+			readmem(tc->mm_struct + OFFSET(mm_struct_pgd),
+				KVADDR, &pgd, sizeof(long), "mm_struct pgd",
+				FAULT_ON_ERROR);
+	}
+
+	switch (machdep->flags & VM_FLAGS)
+	{
+	case VM_L3_4K:
+		return riscv64_vtop_3level_4k(pgd, uvaddr, paddr, verbose);
+	case VM_L4_4K:
+		return riscv64_vtop_4level_4k(pgd, uvaddr, paddr, verbose);
+	case VM_L5_4K:
+		return riscv64_vtop_5level_4k(pgd, uvaddr, paddr, verbose);
+	default:
+		return FALSE;
+	}
+}
+
+static int
+riscv64_kvtop(struct task_context *tc, ulong kvaddr, physaddr_t *paddr, int verbose)
+{
+	ulong kernel_pgd;
+
+	if (!IS_KVADDR(kvaddr))
+		return FALSE;
+
+	if (!vt->vmalloc_start) {
+		*paddr = VTOP(kvaddr);
+		return TRUE;
+	}
+
+	if (!IS_VMALLOC_ADDR(kvaddr)) {
+		*paddr = VTOP(kvaddr);
+		if (!verbose)
+			return TRUE;
+	}
+
+	kernel_pgd = vt->kernel_pgd[0];
+	*paddr = 0;
+
+	switch (machdep->flags & VM_FLAGS)
+	{
+	case VM_L3_4K:
+		return riscv64_vtop_3level_4k((ulong *)kernel_pgd, kvaddr, paddr, verbose);
+	case VM_L4_4K:
+		return riscv64_vtop_4level_4k((ulong *)kernel_pgd, kvaddr, paddr, verbose);
+	case VM_L5_4K:
+		return riscv64_vtop_5level_4k((ulong *)kernel_pgd, kvaddr, paddr, verbose);
+	default:
+		return FALSE;
+	}
+}
+
 void
 riscv64_init(int when)
 {
+	switch (when) {
+	case SETUP_ENV:
+		machdep->process_elf_notes = process_elf64_notes;
+		break;
+
+	case PRE_SYMTAB:
+		machdep->verify_symbol = riscv64_verify_symbol;
+		machdep->machspec = &riscv64_machine_specific;
+		if (pc->flags & KERNEL_DEBUG_QUERY)
+			return;
+
+		machdep->verify_paddr = generic_verify_paddr;
+		machdep->ptrs_per_pgd = PTRS_PER_PGD;
+		break;
+
+	case PRE_GDB:
+		machdep->pagesize = riscv64_get_page_size();
+		machdep->pageshift = ffs(machdep->pagesize) - 1;
+		machdep->pageoffset = machdep->pagesize - 1;
+		machdep->pagemask = ~((ulonglong)machdep->pageoffset);
+		machdep->stacksize = machdep->pagesize << THREAD_SIZE_ORDER;
+
+		riscv64_get_phys_ram_base(machdep->machspec);
+		riscv64_get_struct_page_size(machdep->machspec);
+		riscv64_get_va_bits(machdep->machspec);
+		riscv64_get_va_range(machdep->machspec);
+
+		pt_level_alloc(&machdep->pgd, "cannot malloc pgd space.");
+		pt_level_alloc(&machdep->machspec->p4d, "cannot malloc p4d space.");
+		pt_level_alloc(&machdep->pud, "cannot malloc pud space.");
+		pt_level_alloc(&machdep->pmd, "cannot malloc pmd space.");
+		pt_level_alloc(&machdep->ptbl, "cannot malloc ptbl space.");
+
+		machdep->last_pgd_read = 0;
+		machdep->machspec->last_p4d_read = 0;
+		machdep->last_pud_read = 0;
+		machdep->last_pmd_read = 0;
+		machdep->last_ptbl_read = 0;
+
+		machdep->kvbase = machdep->machspec->page_offset;
+		machdep->identity_map_base = machdep->kvbase;
+		machdep->is_kvaddr = riscv64_is_kvaddr;
+		machdep->is_uvaddr = riscv64_is_uvaddr;
+		machdep->uvtop = riscv64_uvtop;
+		machdep->kvtop = riscv64_kvtop;
+		machdep->cmd_mach = riscv64_cmd_mach;
+
+		machdep->vmalloc_start = riscv64_vmalloc_start;
+		machdep->processor_speed = riscv64_processor_speed;
+		machdep->get_stackbase = generic_get_stackbase;
+		machdep->get_stacktop = generic_get_stacktop;
+		machdep->translate_pte = riscv64_translate_pte;
+		machdep->memory_size = generic_memory_size;
+		machdep->is_task_addr = riscv64_is_task_addr;
+		machdep->get_smp_cpus = riscv64_get_smp_cpus;
+		machdep->value_to_symbol = generic_machdep_value_to_symbol;
+		machdep->show_interrupts = generic_show_interrupts;
+		machdep->get_irq_affinity = generic_get_irq_affinity;
+		machdep->init_kernel_pgd = NULL; /* pgd set by symbol_value("swapper_pg_dir") */
+		break;
+
+	case POST_GDB:
+		machdep->section_size_bits = _SECTION_SIZE_BITS;
+		machdep->max_physmem_bits = _MAX_PHYSMEM_BITS;
+		riscv64_page_type_init();
+
+		if (!machdep->hz)
+			machdep->hz = 250;
+
+		if (symbol_exists("irq_desc"))
+			ARRAY_LENGTH_INIT(machdep->nr_irqs, irq_desc,
+					  "irq_desc", NULL, 0);
+		else if (kernel_symbol_exists("nr_irqs"))
+			get_symbol_data("nr_irqs", sizeof(unsigned int),
+					&machdep->nr_irqs);
+
+		MEMBER_OFFSET_INIT(elf_prstatus_pr_reg, "elf_prstatus",
+				   "pr_reg");
+
+		STRUCT_SIZE_INIT(note_buf, "note_buf_t");
+		break;
+
+	case POST_VM:
+		/*
+		 * crash_notes contains machine specific information about the
+		 * crash. In particular, it contains CPU registers at the time
+		 * of the crash. We need this information to extract correct
+		 * backtraces from the panic task.
+		 */
+		if (!ACTIVE() && !riscv64_init_active_task_regs())
+			error(WARNING,
+				"cannot retrieve registers for active task%s\n\n",
+				kt->cpus > 1 ? "s" : "");
+		break;
+	}
 }
 
+/*
+ * 'help -r' command output
+ */
 void
 riscv64_display_regs_from_elf_notes(int cpu, FILE *ofp)
 {
-- 
2.41.0


From e312ffbea0c454eda2beaf041b7b14eab4a298ec Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:08 +0800
Subject: [PATCH 3/9] RISCV64: Add 'dis' command support

Use generic_dis_filter() function to support dis command implementation.

With this patch, we can get the disassembled code,
crash> dis __crash_kexec
0xffffffff80088580 <__crash_kexec>:     addi    sp,sp,-352
0xffffffff80088582 <__crash_kexec+2>:   sd      s0,336(sp)
0xffffffff80088584 <__crash_kexec+4>:   sd      s1,328(sp)
0xffffffff80088586 <__crash_kexec+6>:   sd      s2,320(sp)
0xffffffff80088588 <__crash_kexec+8>:   addi    s0,sp,352
0xffffffff8008858a <__crash_kexec+10>:  sd      ra,344(sp)
0xffffffff8008858c <__crash_kexec+12>:  sd      s3,312(sp)
0xffffffff8008858e <__crash_kexec+14>:  sd      s4,304(sp)
0xffffffff80088590 <__crash_kexec+16>:  auipc   s2,0x1057
0xffffffff80088594 <__crash_kexec+20>:  addi    s2,s2,-1256
0xffffffff80088598 <__crash_kexec+24>:  ld      a5,0(s2)
0xffffffff8008859c <__crash_kexec+28>:  mv      s1,a0
0xffffffff8008859e <__crash_kexec+30>:  auipc   a0,0xfff

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 1 +
 1 file changed, 1 insertion(+)

diff --git a/riscv64.c b/riscv64.c
index d8de3d5..1e20a09 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -988,6 +988,7 @@ riscv64_init(int when)
 		machdep->is_task_addr = riscv64_is_task_addr;
 		machdep->get_smp_cpus = riscv64_get_smp_cpus;
 		machdep->value_to_symbol = generic_machdep_value_to_symbol;
+		machdep->dis_filter = generic_dis_filter;
 		machdep->show_interrupts = generic_show_interrupts;
 		machdep->get_irq_affinity = generic_get_irq_affinity;
 		machdep->init_kernel_pgd = NULL; /* pgd set by symbol_value("swapper_pg_dir") */
-- 
2.41.0


From 5f8235703e6f086e0cb79b5596ca911cdeac893b Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:09 +0800
Subject: [PATCH 4/9] RISCV64: Add irq command support

With the patch, we can get the irq info,
crash> irq
 IRQ   IRQ_DESC/_DATA      IRQACTION      NAME
 0       (unused)          (unused)
 1   ff60000001329600  ff60000001d17180  "101000.rtc"
 2   ff60000001329800  ff60000001d17680  "ttyS0"
 3   ff60000001329a00  ff60000001c33c00  "virtio0"
 4   ff60000001329c00  ff60000001c33f80  "virtio1"
 5   ff6000000120f400  ff60000001216000  "riscv-timer"

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 1 +
 1 file changed, 1 insertion(+)

diff --git a/riscv64.c b/riscv64.c
index 1e20a09..2355dac 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -989,6 +989,7 @@ riscv64_init(int when)
 		machdep->get_smp_cpus = riscv64_get_smp_cpus;
 		machdep->value_to_symbol = generic_machdep_value_to_symbol;
 		machdep->dis_filter = generic_dis_filter;
+		machdep->dump_irq = generic_dump_irq;
 		machdep->show_interrupts = generic_show_interrupts;
 		machdep->get_irq_affinity = generic_get_irq_affinity;
 		machdep->init_kernel_pgd = NULL; /* pgd set by symbol_value("swapper_pg_dir") */
-- 
2.41.0


From df42b37003adef55162afddfd516f763938da8b4 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:10 +0800
Subject: [PATCH 5/9] RISCV64: Add 'bt' command support

1, Add the implementation to get stack frame from active & inactive
   task's stack.
2, Add 'bt -l' command support get a line number associated with a
   current pc address.
3, Add 'bt -f' command support to display all stack data contained
   in a frame

With the patch, we can get the backtrace,
crash> bt
PID: 113      TASK: ff6000000226c200  CPU: 0    COMMAND: "sh"
 #0 [ff20000010333b90] riscv_crash_save_regs at ffffffff800078f8
 #1 [ff20000010333cf0] panic at ffffffff806578c6
 #2 [ff20000010333d50] sysrq_reset_seq_param_set at ffffffff8038c03c
 #3 [ff20000010333da0] __handle_sysrq at ffffffff8038c604
 #4 [ff20000010333e00] write_sysrq_trigger at ffffffff8038cae4
 #5 [ff20000010333e20] proc_reg_write at ffffffff801b7ee8
 #6 [ff20000010333e40] vfs_write at ffffffff80152bb2
 #7 [ff20000010333e80] ksys_write at ffffffff80152eda
 #8 [ff20000010333ed0] sys_write at ffffffff80152f52

crash> bt -l
PID: 113      TASK: ff6000000226c200  CPU: 0    COMMAND: "sh"
 #0 [ff20000010333b90] riscv_crash_save_regs at ffffffff800078f8
    /buildroot/qemu_riscv64_virt_defconfig/build/linux-custom/arch/riscv/kernel/crash_save_regs.S: 47
 #1 [ff20000010333cf0] panic at ffffffff806578c6
    /buildroot/qemu_riscv64_virt_defconfig/build/linux-custom/kernel/panic.c: 276
 ... ...

crash> bt -f
PID: 113      TASK: ff6000000226c200  CPU: 0    COMMAND: "sh"
 #0 [ff20000010333b90] riscv_crash_save_regs at ffffffff800078f8
    [PC: ffffffff800078f8 RA: ffffffff806578c6 SP: ff20000010333b90 SIZE: 352]
    ff20000010333b90: ff20000010333bb0 ffffffff800078f8
    ff20000010333ba0: ffffffff8008862c ff20000010333b90
    ff20000010333bb0: ffffffff810dde38 ff6000000226c200
    ff20000010333bc0: ffffffff8032be68 0720072007200720
 ... ...

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 netdump.c |  13 +++
 riscv64.c | 283 ++++++++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 296 insertions(+)

diff --git a/netdump.c b/netdump.c
index 4ec12a0..01af145 100644
--- a/netdump.c
+++ b/netdump.c
@@ -42,6 +42,7 @@ static void get_netdump_regs_ppc64(struct bt_info *, ulong *, ulong *);
 static void get_netdump_regs_arm(struct bt_info *, ulong *, ulong *);
 static void get_netdump_regs_arm64(struct bt_info *, ulong *, ulong *);
 static void get_netdump_regs_mips(struct bt_info *, ulong *, ulong *);
+static void get_netdump_regs_riscv(struct bt_info *, ulong *, ulong *);
 static void check_dumpfile_size(char *);
 static int proc_kcore_init_32(FILE *, int);
 static int proc_kcore_init_64(FILE *, int);
@@ -2675,6 +2676,10 @@ get_netdump_regs(struct bt_info *bt, ulong *eip, ulong *esp)
 		return get_netdump_regs_mips(bt, eip, esp);
 		break;
 
+	case EM_RISCV:
+		get_netdump_regs_riscv(bt, eip, esp);
+		break;
+
 	default:
 		error(FATAL, 
 		   "support for ELF machine type %d not available\n",
@@ -2931,6 +2936,8 @@ display_regs_from_elf_notes(int cpu, FILE *ofp)
 		mips_display_regs_from_elf_notes(cpu, ofp);
 	} else if (machine_type("MIPS64")) {
 		mips64_display_regs_from_elf_notes(cpu, ofp);
+	} else if (machine_type("RISCV64")) {
+		riscv64_display_regs_from_elf_notes(cpu, ofp);
 	}
 }
 
@@ -3877,6 +3884,12 @@ get_netdump_regs_mips(struct bt_info *bt, ulong *eip, ulong *esp)
 	machdep->get_stack_frame(bt, eip, esp);
 }
 
+static void
+get_netdump_regs_riscv(struct bt_info *bt, ulong *eip, ulong *esp)
+{
+	machdep->get_stack_frame(bt, eip, esp);
+}
+
 int 
 is_partial_netdump(void)
 {
diff --git a/riscv64.c b/riscv64.c
index 2355dac..4c9b35b 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -33,6 +33,17 @@ static int riscv64_uvtop(struct task_context *tc, ulong vaddr,
 static int riscv64_kvtop(struct task_context *tc, ulong kvaddr,
 			  physaddr_t *paddr, int verbose);
 static void riscv64_cmd_mach(void);
+static void riscv64_stackframe_init(void);
+static void riscv64_back_trace_cmd(struct bt_info *bt);
+static int riscv64_get_dumpfile_stack_frame(struct bt_info *bt,
+					     ulong *nip, ulong *ksp);
+static void riscv64_get_stack_frame(struct bt_info *bt, ulong *pcp,
+				     ulong *spp);
+static int riscv64_get_frame(struct bt_info *bt, ulong *pcp,
+			      ulong *spp);
+static void riscv64_display_full_frame(struct bt_info *bt,
+				        struct riscv64_unwind_frame *current,
+				        struct riscv64_unwind_frame *previous);
 static int riscv64_translate_pte(ulong, void *, ulonglong);
 static int riscv64_init_active_task_regs(void);
 static int riscv64_get_crash_notes(void);
@@ -498,6 +509,275 @@ no_page:
 	return FALSE;
 }
 
+/*
+ * 'bt -f' command output
+ * Display all stack data contained in a frame
+ */
+static void
+riscv64_display_full_frame(struct bt_info *bt, struct riscv64_unwind_frame *current,
+			  struct riscv64_unwind_frame *previous)
+{
+	int i, u_idx;
+	ulong *up;
+	ulong words, addr;
+	char buf[BUFSIZE];
+
+	if (previous->sp < current->sp)
+		return;
+
+	if (!(INSTACK(previous->sp, bt) && INSTACK(current->sp, bt)))
+		return;
+
+	words = (previous->sp - current->sp) / sizeof(ulong) + 1;
+	addr = current->sp;
+	u_idx = (current->sp - bt->stackbase) / sizeof(ulong);
+
+	for (i = 0; i < words; i++, u_idx++) {
+		if (!(i & 1))
+			fprintf(fp, "%s    %lx: ", i ? "\n" : "", addr);
+
+		up = (ulong *)(&bt->stackbuf[u_idx*sizeof(ulong)]);
+		fprintf(fp, "%s ", format_stack_entry(bt, buf, *up, 0));
+		addr += sizeof(ulong);
+	}
+	fprintf(fp, "\n");
+}
+
+static void
+riscv64_stackframe_init(void)
+{
+	long task_struct_thread = MEMBER_OFFSET("task_struct", "thread");
+
+	/* from arch/riscv/include/asm/processor.h */
+	long thread_reg_ra = MEMBER_OFFSET("thread_struct", "ra");
+	long thread_reg_sp = MEMBER_OFFSET("thread_struct", "sp");
+	long thread_reg_fp = MEMBER_OFFSET("thread_struct", "s");
+
+	if ((task_struct_thread == INVALID_OFFSET) ||
+	    (thread_reg_ra == INVALID_OFFSET) ||
+	    (thread_reg_sp == INVALID_OFFSET) ||
+	    (thread_reg_fp == INVALID_OFFSET) )
+		error(FATAL,
+		      "cannot determine thread_struct offsets\n");
+
+	ASSIGN_OFFSET(task_struct_thread_context_pc) =
+		task_struct_thread + thread_reg_ra;
+	ASSIGN_OFFSET(task_struct_thread_context_sp) =
+		task_struct_thread + thread_reg_sp;
+	ASSIGN_OFFSET(task_struct_thread_context_fp) =
+		task_struct_thread + thread_reg_fp;
+}
+
+static void
+riscv64_dump_backtrace_entry(struct bt_info *bt, struct syment *sym,
+			     struct riscv64_unwind_frame *current,
+			     struct riscv64_unwind_frame *previous, int level)
+{
+	const char *name = sym ? sym->name : "(invalid)";
+	struct load_module *lm;
+	char *name_plus_offset = NULL;
+	struct syment *symp;
+	ulong symbol_offset;
+	char buf[BUFSIZE];
+
+	if (bt->flags & BT_SYMBOL_OFFSET) {
+		symp = value_search(current->pc, &symbol_offset);
+
+		if (symp && symbol_offset)
+			name_plus_offset =
+				value_to_symstr(current->pc, buf, bt->radix);
+	}
+
+	fprintf(fp, "%s#%d [%016lx] %s at %016lx",
+		level < 10 ? " " : "",
+		level,
+		current->sp,
+		name_plus_offset ? name_plus_offset : name,
+		current->pc);
+
+	if (module_symbol(current->pc, NULL, &lm, NULL, 0))
+		fprintf(fp, " [%s]", lm->mod_name);
+
+	fprintf(fp, "\n");
+
+	/*
+	 * 'bt -l', get a line number associated with a current pc address.
+	 */
+	if (bt->flags & BT_LINE_NUMBERS) {
+		get_line_number(current->pc, buf, FALSE);
+		if (strlen(buf))
+			fprintf(fp, "    %s\n", buf);
+	}
+
+	/* bt -f */
+	if (bt->flags & BT_FULL) {
+		fprintf(fp, "    "
+			"[PC: %016lx RA: %016lx SP: %016lx SIZE: %ld]\n",
+			current->pc,
+			previous->pc,
+			current->sp,
+			previous->sp - current->sp);
+		riscv64_display_full_frame(bt, current, previous);
+	}
+}
+
+/*
+ * Unroll a kernel stack.
+ */
+static void
+riscv64_back_trace_cmd(struct bt_info *bt)
+{
+	struct riscv64_unwind_frame current, previous;
+	struct stackframe curr_frame;
+	int level = 0;
+
+	if (bt->flags & BT_REGS_NOT_FOUND)
+		return;
+
+	current.pc = bt->instptr;
+	current.sp = bt->stkptr;
+	current.fp = bt->frameptr;
+
+	if (!INSTACK(current.sp, bt))
+		return;
+
+	for (;;) {
+		struct syment *symbol = NULL;
+		struct stackframe *frameptr;
+		ulong low, high;
+		ulong offset;
+
+		if (CRASHDEBUG(8))
+			fprintf(fp, "level %d pc %#lx sp %lx fp 0x%lx\n",
+				level, current.pc, current.sp, current.fp);
+
+		/* Validate frame pointer */
+		low = current.sp + sizeof(struct stackframe);
+		high = bt->stacktop;
+		if (current.fp < low || current.fp > high || current.fp & 0x7) {
+			if (CRASHDEBUG(8))
+				fprintf(fp, "fp 0x%lx sp 0x%lx low 0x%lx high 0x%lx\n",
+					current.fp, current.sp, low, high);
+			return;
+		}
+
+		symbol = value_search(current.pc, &offset);
+		if (!symbol)
+			return;
+
+		frameptr = (struct stackframe *)current.fp - 1;
+		if (!readmem((ulong)frameptr, KVADDR, &curr_frame,
+		    sizeof(curr_frame), "get stack frame", RETURN_ON_ERROR))
+			return;
+
+		previous.pc = curr_frame.ra;
+		previous.fp = curr_frame.fp;
+		previous.sp = current.fp;
+
+		riscv64_dump_backtrace_entry(bt, symbol, &current, &previous, level++);
+
+		current.pc = previous.pc;
+		current.fp = previous.fp;
+		current.sp = previous.sp;
+
+		if (CRASHDEBUG(8))
+			fprintf(fp, "next %d pc %#lx sp %#lx fp %lx\n",
+				level, current.pc, current.sp, current.fp);
+	}
+}
+
+/*
+ * Get a stack frame combination of pc and ra from the most relevant spot.
+ */
+static void
+riscv64_get_stack_frame(struct bt_info *bt, ulong *pcp, ulong *spp)
+{
+	ulong ksp = 0, nip = 0;
+	int ret = 0;
+
+	if (DUMPFILE() && is_task_active(bt->task))
+		ret = riscv64_get_dumpfile_stack_frame(bt, &nip, &ksp);
+	else
+		ret = riscv64_get_frame(bt, &nip, &ksp);
+
+	if (!ret)
+		error(WARNING, "cannot determine starting stack frame for task %lx\n",
+			bt->task);
+
+	if (pcp)
+		*pcp = nip;
+	if (spp)
+		*spp = ksp;
+}
+
+/*
+ * Get the starting point for the active cpu in a diskdump.
+ */
+static int
+riscv64_get_dumpfile_stack_frame(struct bt_info *bt, ulong *nip, ulong *ksp)
+{
+	const struct machine_specific *ms = machdep->machspec;
+	struct riscv64_register *regs;
+	ulong epc, sp;
+
+	if (!ms->crash_task_regs) {
+		bt->flags |= BT_REGS_NOT_FOUND;
+		return FALSE;
+	}
+
+	/*
+	 * We got registers for panic task from crash_notes. Just return them.
+	 */
+	regs = &ms->crash_task_regs[bt->tc->processor];
+	epc = regs->regs[RISCV64_REGS_EPC];
+	sp = regs->regs[RISCV64_REGS_SP];
+
+	/*
+	 * Set stack frame ptr.
+	 */
+	bt->frameptr = regs->regs[RISCV64_REGS_FP];
+
+	if (nip)
+		*nip = epc;
+	if (ksp)
+		*ksp = sp;
+
+	bt->machdep = regs;
+
+	return TRUE;
+}
+
+/*
+ * Do the work for riscv64_get_stack_frame() for non-active tasks.
+ * Get SP and PC values for idle tasks.
+ */
+static int
+riscv64_get_frame(struct bt_info *bt, ulong *pcp, ulong *spp)
+{
+	if (!bt->tc || !(tt->flags & THREAD_INFO))
+		return FALSE;
+
+	if (!readmem(bt->task + OFFSET(task_struct_thread_context_pc),
+		     KVADDR, pcp, sizeof(*pcp),
+		     "thread_struct.ra",
+		     RETURN_ON_ERROR))
+		return FALSE;
+
+	if (!readmem(bt->task + OFFSET(task_struct_thread_context_sp),
+		     KVADDR, spp, sizeof(*spp),
+		     "thread_struct.sp",
+		     RETURN_ON_ERROR))
+		return FALSE;
+
+	if (!readmem(bt->task + OFFSET(task_struct_thread_context_fp),
+		     KVADDR, &bt->frameptr, sizeof(bt->frameptr),
+		     "thread_struct.fp",
+		     RETURN_ON_ERROR))
+		return FALSE;
+
+	return TRUE;
+}
+
 static int
 riscv64_vtop_4level_4k(ulong *pgd, ulong vaddr, physaddr_t *paddr, int verbose)
 {
@@ -978,6 +1258,8 @@ riscv64_init(int when)
 		machdep->uvtop = riscv64_uvtop;
 		machdep->kvtop = riscv64_kvtop;
 		machdep->cmd_mach = riscv64_cmd_mach;
+		machdep->get_stack_frame = riscv64_get_stack_frame;
+		machdep->back_trace = riscv64_back_trace_cmd;
 
 		machdep->vmalloc_start = riscv64_vmalloc_start;
 		machdep->processor_speed = riscv64_processor_speed;
@@ -998,6 +1280,7 @@ riscv64_init(int when)
 	case POST_GDB:
 		machdep->section_size_bits = _SECTION_SIZE_BITS;
 		machdep->max_physmem_bits = _MAX_PHYSMEM_BITS;
+		riscv64_stackframe_init();
 		riscv64_page_type_init();
 
 		if (!machdep->hz)
-- 
2.41.0


From 693715ee208f1beba459e90fbef8899799586ce1 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:11 +0800
Subject: [PATCH 6/9] RISCV64: Add 'help -r' command support

Add support form printing out the registers from the dump file.

With the patch, we can get the regs,
crash> help -r
CPU 0:
epc : 00ffffffa5537400 ra : ffffffff80088620 sp : ff2000001039bb90
 gp : ffffffff810dde38 tp : ff60000002269600 t0 : ffffffff8032be5c
 t1 : 0720072007200720 t2 : 666666666666663c s0 : ff2000001039bcf0
 s1 : 0000000000000000 a0 : ff2000001039bb98 a1 : 0000000000000001
 a2 : 0000000000000010 a3 : 0000000000000000 a4 : 0000000000000000
 a5 : ff60000001c7d000 a6 : 000000000000003c a7 : ffffffff8035c998
 s2 : ffffffff810df0a8 s3 : ffffffff810df718 s4 : ff2000001039bb98
 s5 : 0000000000000000 s6 : 0000000000000007 s7 : ffffffff80c4a468
 s8 : 00fffffffde45410 s9 : 0000000000000007 s10: 00aaaaaad1640700
 s11: 0000000000000001 t3 : ff60000001218f00 t4 : ff60000001218f00
 t5 : ff60000001218000 t6 : ff2000001039b988

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 38 ++++++++++++++++++++++++++++++++++++++
 1 file changed, 38 insertions(+)

diff --git a/riscv64.c b/riscv64.c
index 4c9b35b..6d1d3b5 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -1320,6 +1320,44 @@ riscv64_init(int when)
 void
 riscv64_display_regs_from_elf_notes(int cpu, FILE *ofp)
 {
+	const struct machine_specific *ms = machdep->machspec;
+	struct riscv64_register *regs;
+
+	if (!ms->crash_task_regs) {
+		error(INFO, "registers not collected for cpu %d\n", cpu);
+		return;
+	}
+
+	regs = &ms->crash_task_regs[cpu];
+	if (!regs->regs[RISCV64_REGS_SP] && !regs->regs[RISCV64_REGS_EPC]) {
+		error(INFO, "registers not collected for cpu %d\n", cpu);
+		return;
+	}
+
+	/* Print riscv64 32 regs */
+	fprintf(ofp,
+		"epc : " REG_FMT " ra : " REG_FMT " sp : " REG_FMT "\n"
+		" gp : " REG_FMT " tp : " REG_FMT " t0 : " REG_FMT "\n"
+		" t1 : " REG_FMT " t2 : " REG_FMT " s0 : " REG_FMT "\n"
+		" s1 : " REG_FMT " a0 : " REG_FMT " a1 : " REG_FMT "\n"
+		" a2 : " REG_FMT " a3 : " REG_FMT " a4 : " REG_FMT "\n"
+		" a5 : " REG_FMT " a6 : " REG_FMT " a7 : " REG_FMT "\n"
+		" s2 : " REG_FMT " s3 : " REG_FMT " s4 : " REG_FMT "\n"
+		" s5 : " REG_FMT " s6 : " REG_FMT " s7 : " REG_FMT "\n"
+		" s8 : " REG_FMT " s9 : " REG_FMT " s10: " REG_FMT "\n"
+		" s11: " REG_FMT " t3 : " REG_FMT " t4 : " REG_FMT "\n"
+		" t5 : " REG_FMT " t6 : " REG_FMT "\n",
+		regs->regs[0],  regs->regs[1],  regs->regs[2],
+		regs->regs[3],  regs->regs[4],  regs->regs[5],
+		regs->regs[6],  regs->regs[7],  regs->regs[8],
+		regs->regs[9],  regs->regs[10], regs->regs[11],
+		regs->regs[12], regs->regs[13], regs->regs[14],
+		regs->regs[15], regs->regs[16], regs->regs[17],
+		regs->regs[18], regs->regs[19], regs->regs[20],
+		regs->regs[21], regs->regs[22], regs->regs[23],
+		regs->regs[24], regs->regs[25], regs->regs[26],
+		regs->regs[27], regs->regs[28], regs->regs[29],
+		regs->regs[30], regs->regs[31]);
 }
 
 #else /* !RISCV64 */
-- 
2.41.0


From 58fe88d290e77838f5fece4cae3836b21ef4f780 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:12 +0800
Subject: [PATCH 7/9] RISCV64: Add 'help -m/M' command support

Add riscv64_dump_machdep_table() implementation, display machdep_table.

crash> help -m
              flags: 80 ()
             kvbase: ff60000000000000
  identity_map_base: ff60000000000000
           pagesize: 4096
          pageshift: 12
           pagemask: fffffffffffff000
         pageoffset: fff
        pgdir_shift: 48
       ptrs_per_pgd: 512
       ptrs_per_pte: 512
          stacksize: 16384
                 hz: 250
            memsize: 1071644672 (0x3fe00000)
               bits: 64
         back_trace: riscv64_back_trace_cmd()
    processor_speed: riscv64_processor_speed()
              uvtop: riscv64_uvtop()
              kvtop: riscv64_kvtop()
    get_stack_frame: riscv64_get_stack_frame()
      get_stackbase: generic_get_stackbase()
       get_stacktop: generic_get_stacktop()
      translate_pte: riscv64_translate_pte()
        memory_size: generic_memory_size()
      vmalloc_start: riscv64_vmalloc_start()
       is_task_addr: riscv64_is_task_addr()
      verify_symbol: riscv64_verify_symbol()
         dis_filter: generic_dis_filter()
           dump_irq: generic_dump_irq()
    show_interrupts: generic_show_interrupts()
   get_irq_affinity: generic_get_irq_affinity()
           cmd_mach: riscv64_cmd_mach()
       get_smp_cpus: riscv64_get_smp_cpus()
          is_kvaddr: riscv64_is_kvaddr()
          is_uvaddr: riscv64_is_uvaddr()
       verify_paddr: generic_verify_paddr()
    init_kernel_pgd: NULL
    value_to_symbol: generic_machdep_value_to_symbol()
  line_number_hooks: NULL
      last_pgd_read: ffffffff810e9000
      last_p4d_read: 81410000
      last_pud_read: 81411000
      last_pmd_read: 81412000
     last_ptbl_read: 81415000
                pgd: 560d586f3ab0
                p4d: 560d586f4ac0
                pud: 560d586f5ad0
                pmd: 560d586f6ae0
               ptbl: 560d586f7af0
  section_size_bits: 27
   max_physmem_bits: 56
  sections_per_root: 0
           machspec: 560d57d204a0

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 60 ++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 59 insertions(+), 1 deletion(-)

diff --git a/riscv64.c b/riscv64.c
index 6d1d3b5..5e8c7d1 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -132,7 +132,65 @@ riscv64_verify_symbol(const char *name, ulong value, char type)
 void
 riscv64_dump_machdep_table(ulong arg)
 {
-	/* TODO: */
+	int others = 0;
+
+	fprintf(fp, "              flags: %lx (", machdep->flags);
+	if (machdep->flags & KSYMS_START)
+		fprintf(fp, "%sKSYMS_START", others++ ? "|" : "");
+	fprintf(fp, ")\n");
+
+	fprintf(fp, "             kvbase: %lx\n", machdep->kvbase);
+	fprintf(fp, "  identity_map_base: %lx\n", machdep->identity_map_base);
+	fprintf(fp, "           pagesize: %d\n", machdep->pagesize);
+	fprintf(fp, "          pageshift: %d\n", machdep->pageshift);
+	fprintf(fp, "           pagemask: %llx\n", machdep->pagemask);
+	fprintf(fp, "         pageoffset: %lx\n", machdep->pageoffset);
+	fprintf(fp, "        pgdir_shift: %ld\n", machdep->machspec->va_bits - 9);
+	fprintf(fp, "       ptrs_per_pgd: %u\n", PTRS_PER_PGD);
+	fprintf(fp, "       ptrs_per_pte: %d\n", PTRS_PER_PTE);
+	fprintf(fp, "          stacksize: %ld\n", machdep->stacksize);
+	fprintf(fp, "                 hz: %d\n", machdep->hz);
+	fprintf(fp, "            memsize: %ld (0x%lx)\n",
+		machdep->memsize, machdep->memsize);
+	fprintf(fp, "               bits: %d\n", machdep->bits);
+	fprintf(fp, "         back_trace: riscv64_back_trace_cmd()\n");
+	fprintf(fp, "    processor_speed: riscv64_processor_speed()\n");
+	fprintf(fp, "              uvtop: riscv64_uvtop()\n");
+	fprintf(fp, "              kvtop: riscv64_kvtop()\n");
+	fprintf(fp, "    get_stack_frame: riscv64_get_stack_frame()\n");
+	fprintf(fp, "      get_stackbase: generic_get_stackbase()\n");
+	fprintf(fp, "       get_stacktop: generic_get_stacktop()\n");
+	fprintf(fp, "      translate_pte: riscv64_translate_pte()\n");
+	fprintf(fp, "        memory_size: generic_memory_size()\n");
+	fprintf(fp, "      vmalloc_start: riscv64_vmalloc_start()\n");
+	fprintf(fp, "       is_task_addr: riscv64_is_task_addr()\n");
+	fprintf(fp, "      verify_symbol: riscv64_verify_symbol()\n");
+	fprintf(fp, "         dis_filter: generic_dis_filter()\n");
+	fprintf(fp, "           dump_irq: generic_dump_irq()\n");
+	fprintf(fp, "    show_interrupts: generic_show_interrupts()\n");
+	fprintf(fp, "   get_irq_affinity: generic_get_irq_affinity()\n");
+	fprintf(fp, "           cmd_mach: riscv64_cmd_mach()\n");
+	fprintf(fp, "       get_smp_cpus: riscv64_get_smp_cpus()\n");
+	fprintf(fp, "          is_kvaddr: riscv64_is_kvaddr()\n");
+	fprintf(fp, "          is_uvaddr: riscv64_is_uvaddr()\n");
+	fprintf(fp, "       verify_paddr: generic_verify_paddr()\n");
+	fprintf(fp, "    init_kernel_pgd: NULL\n");
+	fprintf(fp, "    value_to_symbol: generic_machdep_value_to_symbol()\n");
+	fprintf(fp, "  line_number_hooks: NULL\n");
+	fprintf(fp, "      last_pgd_read: %lx\n", machdep->last_pgd_read);
+	fprintf(fp, "      last_p4d_read: %lx\n", machdep->machspec->last_p4d_read);
+	fprintf(fp, "      last_pud_read: %lx\n", machdep->last_pud_read);
+	fprintf(fp, "      last_pmd_read: %lx\n", machdep->last_pmd_read);
+	fprintf(fp, "     last_ptbl_read: %lx\n", machdep->last_ptbl_read);
+	fprintf(fp, "                pgd: %lx\n", (ulong)machdep->pgd);
+	fprintf(fp, "                p4d: %lx\n", (ulong)machdep->machspec->p4d);
+	fprintf(fp, "                pud: %lx\n", (ulong)machdep->pud);
+	fprintf(fp, "                pmd: %lx\n", (ulong)machdep->pmd);
+	fprintf(fp, "               ptbl: %lx\n", (ulong)machdep->ptbl);
+	fprintf(fp, "  section_size_bits: %ld\n", machdep->section_size_bits);
+	fprintf(fp, "   max_physmem_bits: %ld\n", machdep->max_physmem_bits);
+	fprintf(fp, "  sections_per_root: %ld\n", machdep->sections_per_root);
+	fprintf(fp, "           machspec: %lx\n", (ulong)machdep->machspec);
 }
 
 static ulong
-- 
2.41.0


From 1850c7c283f966d1552ee7026bb6fa81e1839464 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:13 +0800
Subject: [PATCH 8/9] RISCV64: Add 'mach' command support

With the patch we can get some basic machine state information,
crash> mach
                MACHINE TYPE: riscv64
                 MEMORY SIZE: 1 GB
                        CPUS: 1
             PROCESSOR SPEED: (unknown)
                          HZ: 250
                   PAGE SIZE: 4096
           KERNEL STACK SIZE: 16384

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 45 ++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 44 insertions(+), 1 deletion(-)

diff --git a/riscv64.c b/riscv64.c
index 5e8c7d1..ff77e41 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -116,10 +116,53 @@ static void riscv64_get_struct_page_size(struct machine_specific *ms)
 	}
 }
 
+/*
+ * "mach" command output.
+ */
+static void
+riscv64_display_machine_stats(void)
+{
+	struct new_utsname *uts;
+	char buf[BUFSIZE];
+	ulong mhz;
+
+	uts = &kt->utsname;
+
+	fprintf(fp, "		MACHINE TYPE: %s\n", uts->machine);
+	fprintf(fp, "		 MEMORY SIZE: %s\n", get_memory_size(buf));
+	fprintf(fp, "			CPUS: %d\n", get_cpus_to_display());
+	fprintf(fp, "	     PROCESSOR SPEED: ");
+	if ((mhz = machdep->processor_speed()))
+		fprintf(fp, "%ld Mhz\n", mhz);
+	else
+		fprintf(fp, "(unknown)\n");
+	fprintf(fp, "			  HZ: %d\n", machdep->hz);
+	fprintf(fp, "		   PAGE SIZE: %d\n", PAGESIZE());
+	fprintf(fp, "	   KERNEL STACK SIZE: %ld\n", STACKSIZE());
+}
+
 static void
 riscv64_cmd_mach(void)
 {
-	/* TODO: */
+	int c;
+
+	while ((c = getopt(argcnt, args, "cmo")) != EOF) {
+		switch (c) {
+		case 'c':
+		case 'm':
+		case 'o':
+			option_not_supported(c);
+			break;
+		default:
+			argerrs++;
+			break;
+		}
+	}
+
+	if (argerrs)
+		cmd_usage(pc->curcmd, SYNOPSIS);
+
+	riscv64_display_machine_stats();
 }
 
 static int
-- 
2.41.0


From 268e1a393fac05ed683068c2e5549d45032703f7 Mon Sep 17 00:00:00 2001
From: Xianting Tian <xianting.tian@linux.alibaba.com>
Date: Thu, 20 Oct 2022 09:50:14 +0800
Subject: [PATCH 9/9] RISCV64: Add the implementation of symbol verify

Verify the symbol to accept or reject a symbol from the kernel namelist.

Signed-off-by: Xianting Tian <xianting.tian@linux.alibaba.com>
---
 riscv64.c | 15 ++++++++++++++-
 1 file changed, 14 insertions(+), 1 deletion(-)

diff --git a/riscv64.c b/riscv64.c
index ff77e41..6b9a688 100644
--- a/riscv64.c
+++ b/riscv64.c
@@ -165,10 +165,23 @@ riscv64_cmd_mach(void)
 	riscv64_display_machine_stats();
 }
 
+/*
+ * Accept or reject a symbol from the kernel namelist.
+ */
 static int
 riscv64_verify_symbol(const char *name, ulong value, char type)
 {
-	/* TODO: */
+	if (CRASHDEBUG(8) && name && strlen(name))
+		fprintf(fp, "%08lx %s\n", value, name);
+
+	if (!(machdep->flags & KSYMS_START)) {
+		if (STREQ(name, "_text") || STREQ(name, "_stext"))
+			machdep->flags |= KSYMS_START;
+
+		return (name && strlen(name) && !STRNEQ(name, "__func__.") &&
+			!STRNEQ(name, "__crc_"));
+	}
+
 	return TRUE;
 }
 
-- 
2.41.0

