Raspberry Pi Config
-------------------
config.ini
::
    [input]
    mtdev_%(name)s = probesysfs,provider=mtdev
    hid_%(name)s = probesysfs,provider=hidinput
    fullscreen=1

reStructuredText Notes
-----------------------

Inline
******
*Emphasis*

**Strong Emphasis**

``Inline literal``

Definition list
    this is the definition

:Field: and The Value

| Line blocks are useful for addresses,
| verse, and adornment-free lists.
|
| Each new line begins with a
| vertical bar ("|").
|     Line breaks and initial indents
|     are preserved.
| Continuation lines are wrapped
  portions of long lines; they begin
  with spaces in place of vertical bars.

Simple table:

=====  =====  ======
   Inputs     Output
------------  ------
  A      B    A or B
=====  =====  ======
False  False  False
True   False  True
False  True   True
True   True   True
=====  =====  ======
