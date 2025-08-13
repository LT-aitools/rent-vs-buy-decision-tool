# Real Estate Decision Tool - Deployment Troubleshooting Guide

## 🎯 Overview

This document provides a complete guide for troubleshooting and fixing deployment issues for the Real Estate Rent vs. Buy Decision Tool. This guide was created after successfully resolving multiple deployment challenges in August 2025.

## 🔍 Problem Summary

The application worked perfectly on localhost but failed to deploy to Streamlit Cloud with various errors including:
- "Oh no. Error running app."
- Health check failures: `dial tcp 127.0.0.1:8501: connect: connection refused`
- Recurring crashes due to parameter mismatches
- Import and path resolution issues

## ✅ Final Solution

**Status:** ✅ RESOLVED  
**Local Deployment:** http://localhost:8501 (Full Featured)  
**Cloud Deployment:** https://real-estate-decision-tool-app.streamlit.app/ (Full Featured)

## 🔧 Root Causes and Fixes

### 1. Parameter Mismatch Crashes

**Problem:** Application crashed due to unused parameters that were removed from UI but still expected by backend functions.

**Error Messages:**
```
Terminal value missing security_deposit_recovery field, using 0.0
```

**Root Cause:** The `security_deposit` and `rental_commission` parameters were intentionally removed from the UI (found via git history), but the NPV analysis functions still expected them.

**Fix Applied:**
```python
# BEFORE: Function signature included unused parameters
def calculate_npv_comparison(
    # ... other params ...
    security_deposit: float = 0.0,
    rental_commission: float = 0.0,
    # ... more params ...
):

# AFTER: Removed unused parameters
def calculate_npv_comparison(
    # ... other params ...
    # Removed: security_deposit and rental_commission
    # ... more params ...
):
```

**Files Modified:**
- `src/calculations/npv_analysis.py` - Removed unused parameters from function signature
- Updated rental initial investment calculation: `rental_initial_investment = moving_costs` (instead of including security deposit + commission)
- Updated rental terminal value to use `0.0` for security deposit

### 2. Streamlit Configuration Conflicts

**Problem:** Multiple `st.set_page_config()` calls causing deployment failures.

**Root Cause:** Both `src/app.py` and `src/app_with_visualizations.py` had page config calls, which Streamlit doesn't allow.

**Fix Applied:**
```python
# BEFORE: Duplicate page configs in multiple files
# src/app.py
st.set_page_config(...)

# src/app_with_visualizations.py  
def main():
    st.set_page_config(...)  # DUPLICATE - CAUSES ERRORS

# AFTER: Single page config in entry point only
# src/app.py
st.set_page_config(...)

# src/app_with_visualizations.py
def main():
    # Removed duplicate page config
    initialize_session()
```

### 3. File Structure and Import Path Issues

**Problem:** Streamlit Cloud couldn't resolve module imports properly due to inconsistent path handling.

**Root Cause:** 
- Multiple entry points with different path configurations
- Conflicting file names causing confusion in Streamlit's auto-detection

**Fix Applied:**
1. **Standardized Entry Point Structure:**
   ```python
   # Add both current and src directories to path
   current_dir = os.path.dirname(os.path.abspath(__file__))
   src_dir = os.path.join(current_dir, 'src')
   sys.path.insert(0, src_dir)
   sys.path.insert(0, current_dir)
   ```

2. **Clean File Naming:**
   - Removed confusing file: `src/app_with_visualizations.py` → `src/app_test_backup.py`
   - Created clear entry point: `app.py` (root level for Streamlit Cloud)
   - Maintained working version: `src/app.py` (for local development)

### 4. Python Version Compatibility

**Problem:** Version mismatch between local development (3.11) and Streamlit Cloud (3.13).

**Fix Applied:**
- Updated `runtime.txt` from `python-3.11` to `python-3.13`
- Verified all dependencies work with Python 3.13

## 📁 Final File Structure

```
rent-vs-buy-decision-tool/
├── app.py                          # Main entry point for Streamlit Cloud
├── runtime.txt                     # python-3.13
├── requirements.txt                # Dependencies with version constraints
├── main.py                        # Fallback entry point
├── streamlit_app.py              # Alternative simple version
├── src/
│   ├── app.py                    # Full featured app for localhost
│   ├── app_full.py              # Complete application logic
│   ├── calculations/
│   │   ├── npv_analysis.py      # FIXED: Removed unused parameters
│   │   ├── mortgage.py
│   │   ├── terminal_value.py
│   │   └── ...
│   ├── components/
│   └── utils/
├── .streamlit/
│   └── config.toml              # Streamlit configuration
└── tests/
```

## 🛠 Deployment Strategy

### Local Development
```bash
cd rent-vs-buy-decision-tool
streamlit run src/app.py
```
- **URL:** http://localhost:8501
- **Features:** Full application with all NPV calculations, charts, exports

### Streamlit Cloud Deployment
- **Entry Point:** `app.py` (root level)
- **Auto-Detection:** Streamlit Cloud automatically finds and runs `app.py`
- **Fallback:** If full app fails, gracefully degrades to simple calculator
- **URL:** https://real-estate-decision-tool-app.streamlit.app/

## 🔄 Troubleshooting Workflow

### Step 1: Identify the Issue Type
```bash
# Check if it's a parameter issue
grep -r "security_deposit\|rental_commission" src/
# Check for import issues  
python -c "import sys; sys.path.append('src'); from calculations.npv_analysis import calculate_npv_comparison"
# Check for config issues
streamlit run src/app.py  # Test locally first
```

### Step 2: Test Minimal Version
1. Create minimal test file:
   ```python
   import streamlit as st
   st.title("Test")
   st.write("Working!")
   ```
2. Deploy to Streamlit Cloud to verify pipeline works
3. Gradually add complexity

### Step 3: Use Graceful Degradation
```python
try:
    # Full featured application
    exec(open(os.path.join(src_dir, 'app_full.py')).read())
except Exception as e:
    # Fallback to simple version
    st.error(f"Full app unavailable: {e}")
    # Simple calculator implementation
```

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] Remove unused parameters from function signatures
- [ ] Single `st.set_page_config()` call per app
- [ ] Clean import paths and sys.path management
- [ ] Test all imports work locally

### File Structure  
- [ ] Clear entry point at root level (`app.py`)
- [ ] No conflicting file names
- [ ] Proper directory structure with `src/` organization

### Configuration
- [ ] `runtime.txt` specifies correct Python version
- [ ] `requirements.txt` has version constraints
- [ ] `.streamlit/config.toml` optimized for cloud deployment

### Testing
- [ ] App works locally: `streamlit run src/app.py`
- [ ] Minimal version works: Test with simple script
- [ ] Dependencies install cleanly: `pip install -r requirements.txt`

## 🐛 Common Issues and Solutions

### "Oh no. Error running app."
- **Cause:** Usually import errors or missing dependencies
- **Solution:** Check logs, test minimal version first, verify all imports

### Health check failures
- **Cause:** App not starting properly, configuration conflicts
- **Solution:** Remove localhost-specific settings, check for duplicate page configs

### Parameter mismatch crashes
- **Cause:** UI changes not reflected in backend functions
- **Solution:** Audit function signatures against actual usage, remove unused parameters

### Import/Path errors
- **Cause:** Inconsistent path handling between local and cloud
- **Solution:** Standardize path setup, test imports independently

## 📈 Performance Optimizations Applied

1. **Dependency Constraints:** Added upper bounds to prevent breaking changes
2. **Graceful Degradation:** Full app falls back to simple calculator if needed
3. **Clean Architecture:** Separated concerns between entry points and application logic
4. **Configuration Optimization:** Streamlit settings optimized for cloud deployment

## 🎯 Success Metrics

- ✅ **Local Deployment:** Works perfectly with full features
- ✅ **Cloud Deployment:** Successfully deployed to Streamlit Cloud
- ✅ **No Crashes:** Eliminated recurring parameter-related crashes
- ✅ **Clean Architecture:** Maintainable file structure and clear entry points
- ✅ **Fallback System:** Graceful degradation if issues occur

## 🔮 Future Maintenance

### When Adding New Features
1. Test locally first: `streamlit run src/app.py`
2. Ensure no unused parameters in function signatures
3. Verify imports work from root level app
4. Test deployment with minimal version first

### When Dependencies Change
1. Update both `requirements.txt` and test locally
2. Verify Python version compatibility in `runtime.txt`
3. Test import changes don't break path resolution

### When File Structure Changes
1. Maintain clear entry points (`app.py` at root)
2. Update path handling if moving modules
3. Test both local and cloud deployment after changes

---

**Created:** August 2025  
**Status:** ✅ Resolved - Both local and cloud deployments working  
**Repository:** https://github.com/LT-aitools/rent-vs-buy-decision-tool