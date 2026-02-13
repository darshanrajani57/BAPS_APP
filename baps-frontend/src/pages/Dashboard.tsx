import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Calendar, Heart, Plus, ArrowRight, FileText } from 'lucide-react';
import { membersApi, sessionsApi, sevasApi } from '../lib/api/client';
import type { Member, Session, Seva } from '../types';

export default function Dashboard() {
  console.log('Dashboard component rendering...');
  
  const [stats, setStats] = useState({
    members: 0,
    activeSessions: 0,
    sevas: 0,
    loading: true,
  });

  useEffect(() => {
    console.log('Dashboard useEffect running, loading stats...');
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      console.log('Loading stats from API...');
      const [members, sessions, sevas] = await Promise.all([
        membersApi.getAll(),
        sessionsApi.getAll(),
        sevasApi.getAll(),
      ]);

      console.log('Stats loaded:', { members: members.length, sessions: sessions.length, sevas: sevas.length });

      setStats({
        members: members.length,
        activeSessions: sessions.filter((s) => s.status === 'ACTIVE').length,
        sevas: sevas.length,
        loading: false,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
      // Set loading to false even on error so UI can render
      setStats((prev) => ({ ...prev, loading: false }));
    }
  };

  const statCards = [
    {
      title: 'Total Members',
      value: stats.members,
      icon: Users,
      color: 'bg-blue-500',
      href: '/members',
    },
    {
      title: 'Active Sessions',
      value: stats.activeSessions,
      icon: Calendar,
      color: 'bg-green-500',
      href: '/sessions',
    },
    {
      title: 'Sevas',
      value: stats.sevas,
      icon: Heart,
      color: 'bg-purple-500',
      href: '/sevas',
    },
  ];

  const quickActions = [
    {
      title: 'Create New Session',
      description: 'Start a new attendance session',
      href: '/sessions/create',
      icon: Plus,
      color: 'bg-primary-600 hover:bg-primary-700',
    },
    {
      title: 'View Members',
      description: 'Browse and manage members',
      href: '/members',
      icon: Users,
      color: 'bg-blue-600 hover:bg-blue-700',
    },
    {
      title: 'Manage Sevas',
      description: 'Create and organize sevas',
      href: '/sevas',
      icon: Heart,
      color: 'bg-purple-600 hover:bg-purple-700',
    },
    {
      title: 'Reports',
      description: 'View session and monthly reports',
      href: '/reports',
      icon: FileText,
      color: 'bg-gray-600 hover:bg-gray-700',
    }
  ];

  if (stats.loading) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading statistics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome to BAPS Attendance System</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link
              key={stat.title}
              to={stat.href}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.title}
                to={action.href}
                className={`${action.color} text-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all transform hover:-translate-y-1`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <Icon size={20} className="mr-2" />
                      <h3 className="font-semibold">{action.title}</h3>
                    </div>
                    <p className="text-sm text-white/90">{action.description}</p>
                  </div>
                  <ArrowRight size={20} className="ml-4" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
