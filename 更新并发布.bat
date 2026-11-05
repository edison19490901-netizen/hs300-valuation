@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Update data and publish to GitHub Pages
echo ============================================
echo.

echo [1/4] Refreshing data (REFRESH=1) ...
set "REFRESH=1"
python analyze.py
if errorlevel 1 goto fail

echo.
echo [2/4] Building dashboard ...
python build_dashboard.py
if errorlevel 1 goto fail

echo.
echo [3/4] Opening local preview ...
start "" "index.html"

echo.
echo [4/4] Checking local changes ...
git status --short
git add -A
git diff --cached --quiet
if errorlevel 1 goto commit
echo No changes to commit.
goto done

:commit
git commit -m "update: monthly data"
if errorlevel 1 goto fail

echo.
set /p CONFIRM=Publish to GitHub now? (Y/N)
if /i not "%CONFIRM%"=="Y" goto done
git push
if errorlevel 1 goto fail

:done
echo.
echo Done. GitHub Pages will refresh in about 1-2 minutes.
pause
exit /b 0

:fail
echo.
echo Failed. Check network / Python / Git, then run again.
pause
exit /b 1
