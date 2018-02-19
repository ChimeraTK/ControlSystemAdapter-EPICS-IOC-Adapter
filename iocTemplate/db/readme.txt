Please save your records file into this directory by the name set in your st.cmd file. Records for ChimeraTK applications will look like this:

record(longin, "$(P)$(R)Counter") {
  field(DTYP, "ChimeraTK")
  field(INP, "@$(APP) counter")
  field(SCAN, "I/O Intr")
}

record(bo, "$(P)$(R)Enabled") {
  field(DTYP, "ChimeraTK")
  field(OUT, "@$(APP) enabled")
  field(ZNAM, "No")
  field(ONAM, "Yes")
}

record(longout, "$(P)$(R)Increment") {
  field(DTYP, "ChimeraTK")
  field(OUT, "@$(APP) increment")
}

record(longout, "$(P)$(R)SleepInterval") {
  field(DTYP, "ChimeraTK")
  field(OUT, "@$(APP) sleepInterval")
}

