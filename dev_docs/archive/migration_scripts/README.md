# Python 2 to 3 Migration Scripts

These scripts were used to migrate EigenD from Python 2.7 to Python 3.14.

## Scripts

**Python 2→3 Syntax Converters:**
- `fix_print_statements.py` - Convert `print x` to `print(x)`
- `fix_raise_statements.py` - Convert `raise Exception, msg` to `raise Exception(msg)`
- `fix_except_statements.py` - Convert `except Exception, e:` to `except Exception as e:`
- `fix_exec_statements.py` - Convert `exec "code"` to `exec("code")`
- `fix_standard_error.py` - Convert `StandardError` to `Exception`
- `fix_async_keyword.py` - Handle async keyword conflicts
- `fix_async_import_final.py` - Fix async import statements
- `fix_func_code.py` - Convert `func_code` to `__code__`
- `fix_types_module.py` - Convert `types.ListType` to `list`, etc.
- `fix_all_prints.py` - Additional print statement fixes
- `fix_remaining_prints.py` - Final print statement cleanup

**Analysis Tools:**
- `compare_scons.py` - Compare SCons 2.5.1 with SCons4 to identify differences (used during SCons migration)

## Status

All migrations are complete. These scripts are kept for reference and potential future use but are no longer needed for the build process.

## Usage

These scripts were run during the migration process. They should not be needed again unless reverting changes or applying similar migrations to other codebases.
