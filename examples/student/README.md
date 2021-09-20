### DEMO

[![asciicast](https://asciinema.org/a/eAjyt5jgDBUUn2BYvtUJzW4qz.svg)](https://asciinema.org/a/eAjyt5jgDBUUn2BYvtUJzW4qz)

### Examples

```bash
$ virtualenv -p python3.6 venv
$ source venv/bin/activate
$ pip install local-judge
```

```bash
$ cd examples/student/wrong/
$ judge
=======+=============================================================
Sample | Accept
=======+=============================================================
     a | ✔
=======+=============================================================
     b | ✔
=======+=============================================================
    gg | ✔
=======+=============================================================
  xxxx | ✘
=======+=============================================================
Total score: 75

[INFO] set `-v 1` to get diff result.
For example: `python3 judge/judge.py -v 1`
```

```bash
$ judge -v 1
=======+=============================================================
Sample | Accept
=======+=============================================================
     a | ✔
=======+=============================================================
     b | ✔
=======+=============================================================
    gg | ✔
=======+=============================================================
  xxxx | ✘
-------+-------------------------------------------------------------
diff --git a/tmp/output/xxxx_1579510539.out b/home/ben/pro/selfpro/local-judge/examples/student/answer/xxxx.out
index 4f6ff86..3a2e3f4 100644
--- a/tmp/output/xxxx_1579510539.out
+++ b/home/ben/pro/selfpro/local-judge/examples/student/answer/xxxx.out
@@ -1 +1 @@
4294967295-1

=======+=============================================================
Total score: 75
```

```bash
$ judge -i xxxx
=======+=============================================================
Sample | Accept
=======+=============================================================
  xxxx | ✘
-------+-------------------------------------------------------------
diff --git a/tmp/output/xxxx_1579510564.out b/home/ben/pro/selfpro/local-judge/examples/student/answer/xxxx.out
index 4f6ff86..3a2e3f4 100644
--- a/tmp/output/xxxx_1579510564.out
+++ b/home/ben/pro/selfpro/local-judge/examples/student/answer/xxxx.out
@@ -1 +1 @@
4294967295-1

=======+=============================================================
Total score: 0
```
