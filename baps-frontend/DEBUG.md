# Debugging Empty Page Issue

## Steps to Debug

1. **Open Browser Console (F12)**
   - Look for any red error messages
   - Check if you see console.log messages like:
     - "main.tsx: Starting app..."
     - "App component rendering..."
     - "Layout component rendering..."
     - "Dashboard component rendering..."

2. **Check Network Tab**
   - See if API requests are being made
   - Check if they're failing (red status codes)
   - Verify backend is running on `http://localhost:5000`

3. **Check Elements Tab**
   - Inspect the `<div id="root">` element
   - See if React has rendered anything inside it
   - Check if there are any elements with styles that might hide content

4. **Common Issues:**

   **Issue: Backend not running**
   - Solution: Start Flask backend: `cd attendance-system && python app.py`
   
   **Issue: CORS errors**
   - Solution: Make sure Flask has `CORS(app)` enabled
   
   **Issue: API URL incorrect**
   - Check `.env` file has: `VITE_API_URL=http://localhost:5000/api`
   - Restart dev server after changing `.env`
   
   **Issue: JavaScript errors**
   - Check browser console for specific error messages
   - Look for import errors or missing dependencies

5. **Quick Test:**
   - Open browser console
   - Type: `document.getElementById('root').innerHTML`
   - If it's empty, React hasn't rendered
   - If it has content, check CSS/styling issues

## What to Report

If the page is still empty, please share:
1. Browser console errors (screenshot or copy text)
2. Network tab - any failed requests?
3. What you see in Elements tab for `<div id="root">`
4. Terminal output from `npm run dev`
