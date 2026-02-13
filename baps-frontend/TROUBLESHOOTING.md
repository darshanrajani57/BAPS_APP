# Troubleshooting Guide

## Common Issues and Solutions

### 1. Node.js Version Error
**Error:** `Vite requires Node.js version 20.19+ or 22.12+`

**Solution:** The project has been configured to work with Node.js 18.18.0. If you still see this error:
- Make sure you've deleted `node_modules` and `package-lock.json`
- Run `npm install` again
- The package.json has been updated with compatible versions

### 2. Pages Not Loading / Navigation Not Working

**Possible Causes:**
1. **Backend not running** - The Flask backend must be running on `http://localhost:5000`
2. **CORS issues** - Make sure Flask-CORS is enabled in your backend
3. **API errors** - Check browser console for API errors

**Solutions:**
1. Start the Flask backend:
   ```bash
   cd attendance-system
   python app.py
   ```

2. Check browser console (F12) for errors:
   - Look for API request errors
   - Check if backend URL is correct
   - Verify CORS headers are present

3. Verify API URL in `.env`:
   ```
   VITE_API_URL=http://localhost:5000/api
   ```

### 3. API Request Failures

**Symptoms:**
- Pages load but show "Failed to load" messages
- Empty data in tables
- Console shows network errors

**Debugging Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Check if API requests are being made
4. Look for:
   - 404 errors (endpoint not found)
   - CORS errors (blocked by browser)
   - 500 errors (backend errors)

**Common Fixes:**
- Ensure backend is running
- Check API endpoint URLs match backend routes
- Verify CORS is enabled: `CORS(app)` in Flask app

### 4. TypeScript Errors

If you see TypeScript compilation errors:
```bash
npm run build
```

Check for:
- Missing type definitions
- Import path errors
- Type mismatches

### 5. Styling Issues (Tailwind Not Working)

If styles aren't applying:
1. Verify `tailwind.config.js` exists
2. Check `postcss.config.js` exists
3. Ensure `index.css` has Tailwind directives:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

### 6. React Router Not Working

If clicking links doesn't navigate:
1. Verify `BrowserRouter` is wrapping routes in `App.tsx`
2. Check that `react-router-dom` is installed
3. Ensure all routes are inside `<Routes>` component

## Debug Mode

The app includes enhanced error handling:
- **Error Boundary** - Catches React errors and displays friendly messages
- **API Interceptors** - Logs all API requests/responses to console
- **Console Logging** - Check browser console for detailed error messages

## Getting Help

1. **Check Browser Console** - Most errors will be logged here
2. **Check Network Tab** - See if API calls are successful
3. **Check Backend Logs** - Flask will show errors in terminal
4. **Verify Environment** - Ensure `.env` file has correct API URL

## Quick Test

To verify everything is working:

1. Start backend:
   ```bash
   cd attendance-system
   python app.py
   ```

2. Start frontend:
   ```bash
   cd baps-frontend
   npm run dev
   ```

3. Open browser to `http://localhost:5173`

4. Check console for:
   - No red errors
   - API requests being made
   - Data loading successfully
