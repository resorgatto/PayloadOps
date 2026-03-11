import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RefreshCcw, Search, Filter, X } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import styles from './ExecutionLogs.module.css';

interface LogEntry {
    id: string;
    workflow_name: string;
    status: 'successful' | 'failed' | 'pending';
    triggered_at: string;
    duration_ms: number;
    payload: any;
    error_message?: string;
}

export function ExecutionLogs() {
    const [search, setSearch] = useState('');
    const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);

    // TanStack Query polling every 5 seconds
    const { data: logs = [], isFetching, refetch } = useQuery<LogEntry[]>({
        queryKey: ['executionLogs'],
        queryFn: async () => {
            // Mock Data
            return [
                { id: 'log_001', workflow_name: 'Stripe to Slack', status: 'successful', triggered_at: new Date().toISOString(), duration_ms: 124, payload: { event: 'charge.succeeded', amount: 2000 } },
                { id: 'log_002', workflow_name: 'Jira Sync', status: 'failed', triggered_at: new Date(Date.now() - 60000).toISOString(), duration_ms: 450, payload: { issue: 'PROJ-123' }, error_message: 'API Rate limit exceeded' },
                { id: 'log_003', workflow_name: 'Lead Capture', status: 'pending', triggered_at: new Date(Date.now() - 120000).toISOString(), duration_ms: 0, payload: { email: 'test@example.com' } },
            ];
        },
        refetchInterval: 5000,
    });

    const filteredLogs = logs.filter(l => l.workflow_name.toLowerCase().includes(search.toLowerCase()) || l.id.includes(search));

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div>
                    <h1 className={styles.title}>Execution Logs</h1>
                    <p className={styles.subtitle}>Monitor webhook events and workflow actions in real-time.</p>
                </div>
                <button className={styles.secondaryButton} onClick={() => refetch()} disabled={isFetching}>
                    <RefreshCcw size={14} className={isFetching ? styles.spin : ''} />
                    <span>Refresh</span>
                </button>
            </header>

            <div className={styles.toolbar}>
                <div className={styles.searchWrapper}>
                    <Search size={16} className={styles.searchIcon} />
                    <input
                        type="text"
                        placeholder="Search by workflow or ID..."
                        className={styles.searchInput}
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <button className={styles.iconButton}><Filter size={16} /> Filter</button>
            </div>

            <div className={styles.tableWrapper}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Workflow</th>
                            <th>Execution ID</th>
                            <th>Duration</th>
                            <th>Triggered At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredLogs.map(log => (
                            <Dialog.Root key={log.id} open={selectedLog?.id === log.id} onOpenChange={(open) => !open && setSelectedLog(null)}>
                                <Dialog.Trigger asChild>
                                    <tr className={styles.clickableRow} onClick={() => setSelectedLog(log)}>
                                        <td>
                                            <span className={`${styles.statusDot} ${styles[`status--${log.status}`]}`}></span>
                                            <span className={styles.statusText}>{log.status}</span>
                                        </td>
                                        <td className={styles.cellBold}>{log.workflow_name}</td>
                                        <td className={styles.cellMuted}>{log.id}</td>
                                        <td className={styles.cellMuted}>{log.duration_ms}ms</td>
                                        <td className={styles.cellMuted}>{new Date(log.triggered_at).toLocaleString()}</td>
                                    </tr>
                                </Dialog.Trigger>

                                {/* Right Drawer showing details */}
                                <Dialog.Portal>
                                    <Dialog.Overlay className={styles.drawerOverlay} />
                                    <Dialog.Content className={styles.drawerContent}>
                                        <div className={styles.drawerHeader}>
                                            <div>
                                                <Dialog.Title className={styles.drawerTitle}>Execution Details</Dialog.Title>
                                                <Dialog.Description className={styles.drawerDesc}>ID: {log.id}</Dialog.Description>
                                            </div>
                                            <Dialog.Close asChild>
                                                <button className={styles.closeBtn}><X size={18} /></button>
                                            </Dialog.Close>
                                        </div>

                                        <div className={styles.drawerBody}>
                                            {log.error_message && (
                                                <div className={styles.errorAlert}>
                                                    <strong>Error:</strong> {log.error_message}
                                                </div>
                                            )}

                                            <div className={styles.sectionHeader}>Headers & Context</div>
                                            <div className={styles.jsonWrapper}>
                                                <pre>{JSON.stringify({ "User-Agent": "Stripe/1.0", "Content-Type": "application/json" }, null, 2)}</pre>
                                            </div>

                                            <div className={styles.sectionHeader}>Payload Data</div>
                                            <div className={styles.jsonWrapper}>
                                                <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                                            </div>
                                        </div>
                                    </Dialog.Content>
                                </Dialog.Portal>
                            </Dialog.Root>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
