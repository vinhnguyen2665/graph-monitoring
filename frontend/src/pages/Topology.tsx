import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { Background, Controls, MarkerType, Position } from 'reactflow';
import type { Edge, Node } from 'reactflow';
import 'reactflow/dist/style.css';
import { api } from '../api/axios';
import { message } from 'antd';
import { useTranslation } from '../i18n/LanguageContext';


const Topology: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const { t } = useTranslation();

  const getClientIp = (l: any) => {
    if (l.real_ip && l.real_ip !== '-') return l.real_ip;
    if (l.cf_ip && l.cf_ip !== '-') return l.cf_ip;
    if (l.xff && l.xff !== '-') return l.xff;
    if (l.remote && l.remote !== '-') return l.remote;
    return 'Unknown';
  };

  const processData = useCallback((data: any, isHistorical: boolean) => {
    setNodes((prevNodes) => {
      const nextNodes = [...prevNodes];
      const nextNodeIds = new Set(nextNodes.map(n => n.id));

      if (!isHistorical) {
        // Find active clients from the new active logs
        const activeClients = new Set<string>();
        data.data.forEach((log: any) => {
          activeClients.add(getClientIp(log));
        });

        // Find existing clients to remove if not active
        const existingClients = nextNodes.filter(n => n.type === 'input' && n.id.startsWith('client-'));
        for (const clientNode of existingClients) {
          const ip = clientNode.id.replace('client-', '');
          if (!activeClients.has(ip)) {
            // Remove it
            const idx = nextNodes.findIndex(n => n.id === clientNode.id);
            if (idx !== -1) nextNodes.splice(idx, 1);
          }
        }

        // Re-calculate Y positions for all remaining clients to close gaps
        const remainingClients = nextNodes.filter(n => n.type === 'input' && n.id.startsWith('client-'));
        // Sort by current Y to maintain relative order
        remainingClients.sort((a, b) => a.position.y - b.position.y);

        let currentClientY = 0;
        for (const clientNode of remainingClients) {
          clientNode.position.y = currentClientY;
          currentClientY += 100;
        }

        // Add new active clients
        activeClients.forEach(ip => {
          const id = `client-${ip}`;
          if (!nextNodeIds.has(id)) {
            nextNodes.push({
              id,
              position: { x: 0, y: currentClientY },
              data: { label: `Client: ${ip}` },
              type: 'input',
              sourcePosition: Position.Right
            });
            nextNodeIds.add(id);
            currentClientY += 100;
          }
        });
      }

      // Add Nginx and Upstreams if they are new (from both historical and active data)
      let maxNginxY = -100;
      let maxUpstreamY = -100;
      nextNodes.forEach(n => {
        if (n.type === 'default' && n.id.startsWith('nginx-') && n.position.y > maxNginxY) {
          maxNginxY = n.position.y;
        }
        if (n.type === 'output' && n.id.startsWith('upstream-') && n.position.y > maxUpstreamY) {
          maxUpstreamY = n.position.y;
        }
      });

      data.data.forEach((log: any) => {
        const protocol = log.scheme || 'http';
        const targetHost = log.host || log.server_name || 'unknown';
        const nginxId = `nginx-${protocol}://${targetHost}`;

        if (!nextNodeIds.has(nginxId)) {
          maxNginxY += 100;
          nextNodes.push({
            id: nginxId,
            position: { x: 300, y: maxNginxY },
            // data: { label: `Nginx: ${protocol}://${targetHost}` },
            data: { label: `${protocol}://${targetHost}` },
            type: 'default',
            targetPosition: Position.Left,
            sourcePosition: Position.Right
          });
          nextNodeIds.add(nginxId);
        }

        const upstream = log.upstream_addr || log.destination;
        if (upstream && upstream !== '-') {
          const upstreamId = `upstream-${upstream}`;
          if (!nextNodeIds.has(upstreamId)) {
            maxUpstreamY += 100;
            nextNodes.push({
              id: upstreamId,
              position: { x: 600, y: maxUpstreamY },
              data: { label: `Upstream: ${upstream}` },
              type: 'output',
              targetPosition: Position.Left
            });
            nextNodeIds.add(upstreamId);
          }
        }
      });

      return nextNodes;
    });

    setEdges((prevEdges) => {
      const nextEdges = [...prevEdges];
      const nextEdgeIds = new Set(nextEdges.map(e => e.id));

      if (!isHistorical) {
        // Find active clients
        const activeClients = new Set<string>();
        data.data.forEach((log: any) => {
          activeClients.add(getClientIp(log));
        });

        // Remove edges that belong to removed clients
        for (let i = nextEdges.length - 1; i >= 0; i--) {
          const edge = nextEdges[i];
          if (edge.source.startsWith('client-')) {
            const ip = edge.source.replace('client-', '');
            if (!activeClients.has(ip)) {
              nextEdges.splice(i, 1);
            }
          }
        }

        // Add new edges for active logs
        data.data.forEach((log: any) => {
          const clientIp = getClientIp(log);
          const clientId = `client-${clientIp}`;

          const protocol = log.scheme || 'http';
          const targetHost = log.host || log.server_name || 'unknown';
          const nginxId = `nginx-${protocol}://${targetHost}`;

          if (activeClients.has(clientIp)) {
            const clientNginxEdgeId = `${clientId}-${nginxId}`;
            if (!nextEdgeIds.has(clientNginxEdgeId)) {
              nextEdges.push({
                id: clientNginxEdgeId,
                source: clientId,
                target: nginxId,
                animated: true,
                label: '',
                style: { stroke: '#1890ff' },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#1890ff' }
              });
              nextEdgeIds.add(clientNginxEdgeId);
            }
          }

          const upstream = log.upstream_addr || log.destination;
          if (upstream && upstream !== '-') {
            const upstreamId = `upstream-${upstream}`;
            const nginxUpstreamEdgeId = `${nginxId}-${upstreamId}`;
            if (!nextEdgeIds.has(nginxUpstreamEdgeId)) {
              nextEdges.push({
                id: nginxUpstreamEdgeId,
                source: nginxId,
                target: upstreamId,
                animated: true,
                label: '',
                style: { stroke: log.status >= 400 ? 'red' : 'green' },
                markerEnd: { type: MarkerType.ArrowClosed, color: log.status >= 400 ? 'red' : 'green' }
              });
              nextEdgeIds.add(nginxUpstreamEdgeId);
            } else if (log.status >= 400) {
              const idx = nextEdges.findIndex(e => e.id === nginxUpstreamEdgeId);
              if (idx !== -1 && nextEdges[idx].style?.stroke !== 'red') {
                nextEdges[idx] = {
                  ...nextEdges[idx],
                  style: { stroke: 'red' },
                  markerEnd: { type: MarkerType.ArrowClosed, color: 'red' }
                };
              }
            }
          }
        });
      }

      return nextEdges;
    });
  }, []);

  useEffect(() => {
    // Initial fetch to get historical architecture (Nginx, Upstreams)
    api.get('/logs', { params: { limit: 500 } }).then(res => {
      processData(res.data, true);
    }).catch(() => {
      message.error("Failed to load historical topology");
    });

    // Polling fetch to get active traffic (last N seconds handled by backend)
    const fetchActive = async () => {
      try {
        const { data } = await api.get('/logs', { params: { limit: 500, mode: 'topology' } });
        processData(data, false);
      } catch (e) {
        console.error("Failed to fetch active topology", e);
      }
    };

    const interval = setInterval(fetchActive, 5000);
    // Fetch active immediately as well to populate active clients
    fetchActive();

    return () => clearInterval(interval);
  }, [processData]);

  return (
    <div style={{ padding: 24, height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>{t('topologyTitle')}</h2>
        <p style={{ color: '#8c8c8c', margin: '4px 0 0 0' }}>{t('topologyDesc')}</p>
      </div>
      <div style={{ flex: 1, border: '1px solid #f0f0f0', borderRadius: 8, overflow: 'hidden' }}>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
};

export default Topology;
