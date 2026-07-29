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

  const processData = useCallback((responseData: any, isHistorical: boolean) => {
    if (!responseData) return;
    const logsList = Array.isArray(responseData.data) 
      ? responseData.data 
      : (Array.isArray(responseData) ? responseData : []);
    
    if (logsList.length === 0) return;

    setNodes((prevNodes) => {
      const nextNodes = [...prevNodes];
      const nextNodeIds = new Set(nextNodes.map(n => n.id));

      let currentClientY = nextNodes.filter(n => n.type === 'input').length * 100;
      let maxNginxY = nextNodes.filter(n => n.type === 'default').length * 100;
      let maxUpstreamY = nextNodes.filter(n => n.type === 'output').length * 100;

      logsList.forEach((log: any) => {
        if (!log) return;
        // 1. Client Node
        const clientIp = getClientIp(log);
        const clientId = `client-${clientIp}`;
        if (!nextNodeIds.has(clientId)) {
          nextNodes.push({
            id: clientId,
            position: { x: 0, y: currentClientY },
            data: { label: `Client: ${clientIp}` },
            type: 'input',
            sourcePosition: Position.Right
          });
          nextNodeIds.add(clientId);
          currentClientY += 100;
        }

        // 2. Nginx Node
        const protocol = log.scheme || 'http';
        const targetHost = log.host || log.server_name || 'unknown';
        const nginxId = `nginx-${protocol}://${targetHost}`;
        if (!nextNodeIds.has(nginxId)) {
          nextNodes.push({
            id: nginxId,
            position: { x: 300, y: maxNginxY },
            data: { label: `${protocol}://${targetHost}` },
            type: 'default',
            targetPosition: Position.Left,
            sourcePosition: Position.Right
          });
          nextNodeIds.add(nginxId);
          maxNginxY += 100;
        }

        // 3. Upstream Node
        const upstream = log.upstream_addr || log.destination;
        if (upstream && upstream !== '-' && upstream !== 'client') {
          const upstreamId = `upstream-${upstream}`;
          if (!nextNodeIds.has(upstreamId)) {
            nextNodes.push({
              id: upstreamId,
              position: { x: 600, y: maxUpstreamY },
              data: { label: `Upstream: ${upstream}` },
              type: 'output',
              targetPosition: Position.Left
            });
            nextNodeIds.add(upstreamId);
            maxUpstreamY += 100;
          }
        }
      });

      return nextNodes;
    });

    setEdges((prevEdges) => {
      const nextEdges = [...prevEdges];
      const nextEdgeIds = new Set(nextEdges.map(e => e.id));

      logsList.forEach((log: any) => {
        if (!log) return;
        const clientIp = getClientIp(log);
        const clientId = `client-${clientIp}`;

        const protocol = log.scheme || 'http';
        const targetHost = log.host || log.server_name || 'unknown';
        const nginxId = `nginx-${protocol}://${targetHost}`;

        // Client -> Nginx Edge
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

        // Nginx -> Upstream Edge
        const upstream = log.upstream_addr || log.destination;
        if (upstream && upstream !== '-' && upstream !== 'client') {
          const upstreamId = `upstream-${upstream}`;
          const nginxUpstreamEdgeId = `${nginxId}-${upstreamId}`;
          if (!nextEdgeIds.has(nginxUpstreamEdgeId)) {
            nextEdges.push({
              id: nginxUpstreamEdgeId,
              source: nginxId,
              target: upstreamId,
              animated: true,
              label: '',
              style: { stroke: log.status >= 400 ? '#ff4d4f' : '#52c41a' },
              markerEnd: { type: MarkerType.ArrowClosed, color: log.status >= 400 ? '#ff4d4f' : '#52c41a' }
            });
            nextEdgeIds.add(nginxUpstreamEdgeId);
          } else if (log.status >= 400) {
            const idx = nextEdges.findIndex(e => e.id === nginxUpstreamEdgeId);
            if (idx !== -1 && nextEdges[idx].style?.stroke !== '#ff4d4f') {
              nextEdges[idx] = {
                ...nextEdges[idx],
                style: { stroke: '#ff4d4f' },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#ff4d4f' }
              };
            }
          }
        }
      });

      return nextEdges;
    });
  }, []);

  useEffect(() => {
    // Initial fetch to get historical architecture (Nginx, Upstreams)
    api.get('/logs', { params: { limit: 500 } }).then(res => {
      if (res && res.data) {
        processData(res.data, true);
      }
    }).catch(() => {
      message.error("Failed to load historical topology");
    });

    // Polling fetch to get active traffic (last N seconds handled by backend)
    const fetchActive = async () => {
      try {
        const res = await api.get('/logs', { params: { limit: 500, mode: 'topology' } });
        if (res && res.data) {
          processData(res.data, false);
        }
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
