import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Members from './pages/Members';
import Sessions from './pages/Sessions';
import CreateSession from './pages/CreateSession';
import SessionAttendance from './pages/SessionAttendance';
import SessionReport from './pages/SessionReport';
import Sevas from './pages/Sevas';
import Reports from './pages/Reports';
import MonthlyReports from './pages/MonthlyReports';
import MemberDetail from './pages/members/MemberDetail';

function App() {
  console.log('App component rendering...');
  
  try {
    return (
      <ErrorBoundary>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/members" element={<Members />} />
              <Route path="/members/:id" element={<MemberDetail />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/sessions/create" element={<CreateSession />} />
              <Route path="/sessions/:id" element={<SessionAttendance />} />
              <Route path="/sessions/:id/report" element={<SessionReport />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/reports/monthly" element={<MonthlyReports />} />
              <Route path="/sevas" element={<Sevas />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ErrorBoundary>
    );
  } catch (error) {
    console.error('Error in App component:', error);
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Error Loading App</h1>
        <p>{String(error)}</p>
      </div>
    );
  }
}

export default App;
