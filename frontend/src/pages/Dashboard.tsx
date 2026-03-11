import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/auth';
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import styles from './Dashboard.module.css';

interface Metrics {
    total_executions: number;
    successful: number;
    failed: number;
    pending: number;
    success_rate: number;
    avg_duration_ms: number;
}

// Mock chart data for MVP visualization
const chartData = [
    { name: 'Mon', executions: 4000, failed: 240 },
    { name: 'Tue', executions: 3000, failed: 139 },
    { name: 'Wed', executions: 2000, failed: 980 },
    { name: 'Thu', executions: 2780, failed: 390 },
    { name: 'Fri', executions: 1890, failed: 480 },
    { name: 'Sat', executions: 2390, failed: 380 },
    { name: 'Sun', executions: 3490, failed: 430 },
];

export function Dashboard() {
    const user = useAuthStore((state) => state.user);

    // Example of metrics endpoint query
    const { data: metrics } = useQuery({
        queryKey: ['metricsSummary'],
        queryFn: async () => {
            // Return mock initially if backend requires a real workspace ID header
            // const res = await api.get<Metrics>('/logs/metrics/summary');
            // return res.data;
            return {
                total_executions: 18940,
                successful: 15890,
                failed: 3050,
                pending: 12,
                success_rate: 83.9,
                avg_duration_ms: 104,
            } as Metrics;
        },
    });

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 18) return 'Good afternoon';
        return 'Good evening';
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>
                    {getGreeting()}, {user?.full_name?.split(' ')[0] || user?.username || 'User'}
                </h1>
                <p className={styles.subtitle}>Here's what is happening with your webhook integrations today.</p>
            </header>

            {/* Metrics Grid */}
            <div className={styles.metricsGrid}>
                <div className={styles.metricCard}>
                    <span className={styles.cardLabel}>Total Executions</span>
                    <div className={styles.cardValue}>{metrics?.total_executions.toLocaleString()}</div>
                </div>
                <div className={styles.metricCard}>
                    <span className={styles.cardLabel}>Success Rate</span>
                    <div className={styles.cardValue}>{metrics?.success_rate}%</div>
                </div>
                <div className={styles.metricCard}>
                    <span className={styles.cardLabel}>Avg Duration</span>
                    <div className={styles.cardValue}>{metrics?.avg_duration_ms} ms</div>
                </div>
                <div className={styles.metricCard}>
                    <span className={styles.cardLabel}>Pending Events</span>
                    <div className={styles.cardValue}>{metrics?.pending}</div>
                </div>
            </div>

            {/* Charts Section */}
            <div className={styles.chartsGrid}>
                <div className={styles.chartPanel}>
                    <h3>Execution Volume</h3>
                    <div className={styles.chartWrapper}>
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorExecutions" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--bg-elevated)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }}
                                    itemStyle={{ color: 'var(--text-primary)' }}
                                />
                                <Area type="monotone" dataKey="executions" stroke="var(--primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorExecutions)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className={styles.chartPanel}>
                    <h3>Failed Executions</h3>
                    <div className={styles.chartWrapper}>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--bg-elevated)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }}
                                    itemStyle={{ color: 'var(--error)' }}
                                />
                                <Line type="monotone" dataKey="failed" stroke="var(--error)" strokeWidth={2} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
