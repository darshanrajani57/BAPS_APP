import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

console.log('=== MAIN.TSX STARTING ===');
console.log('Root element exists:', !!document.getElementById('root'));

try {
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Root element #root not found in DOM!');
  }
  
  console.log('Creating React root...');
  const root = createRoot(rootElement);
  
  console.log('Loading App component...');
  
  // Import and render the full app
  import('./App.tsx').then((module) => {
    const App = module.default;
    console.log('App component loaded, rendering...');
    
    root.render(
      <StrictMode>
        <App />
      </StrictMode>
    );
    
    console.log('✅ Full App rendered successfully!');
  }).catch((error) => {
    console.error('❌ Error loading App component:', error);
    
    // Show error on page
    root.render(
      <div style={{ 
        padding: '40px', 
        fontFamily: 'Arial, sans-serif',
        backgroundColor: '#fee',
        minHeight: '100vh'
      }}>
        <h1 style={{ color: '#c00' }}>❌ Error Loading App</h1>
        <p><strong>Error:</strong> {error.message || String(error)}</p>
        <details style={{ marginTop: '20px' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>Show Full Error</summary>
          <pre style={{ 
            background: '#fff', 
            padding: '15px', 
            overflow: 'auto', 
            border: '1px solid #ccc',
            marginTop: '10px'
          }}>
            {error.stack || JSON.stringify(error, null, 2)}
          </pre>
        </details>
        <p style={{ marginTop: '20px' }}>Check the browser console (F12) for more details.</p>
      </div>
    );
  });
  
} catch (error: any) {
  console.error('❌ CRITICAL ERROR:', error);
  
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="padding: 40px; font-family: Arial; background: #fee; border: 2px solid #f00;">
        <h1 style="color: #c00;">❌ CRITICAL ERROR</h1>
        <p><strong>Error:</strong> ${error.message || String(error)}</p>
        <pre style="background: #fff; padding: 10px; overflow: auto; border: 1px solid #ccc;">
${error.stack || 'No stack trace'}
        </pre>
        <p>Open browser console (F12) for more details.</p>
      </div>
    `;
  }
}
