import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useSessionStore } from '@/store/sessionStore'
import { apisService } from '@/services/apis'
import { GitBranch, RefreshCw, Terminal, AlertTriangle, Maximize2 } from 'lucide-react'
import clsx from 'clsx'

const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const NODE_COLOR: Record<string, string> = {
  python:     '#3b82f6',
  typescript: '#22c55e',
  javascript: '#f97316',
}

export const DependencyGraphPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const svgRef  = useRef<SVGSVGElement>(null)
  const simRef  = useRef<any>(null)
  const zoomRef = useRef<any>(null)   // stores the d3.zoom instance for reset

  const [nodes,      setNodes]      = useState<any[]>([])
  const [edges,      setEdges]      = useState<any[]>([])
  const [stats,      setStats]      = useState<any>(null)
  const [loading,    setLoading]    = useState(false)
  const [done,       setDone]       = useState(false)
  const [error,      setError]      = useState<string | null>(null)
  const [selected,   setSelected]   = useState<any>(null)
  const [filterType, setFilterType] = useState('all')

  const load = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await apisService.graph(currentSessionId)
      const d   = (res.data as any).data
      setNodes(d.nodes || [])
      setEdges(d.edges || [])
      setStats(d.stats || null)
      setDone(true)
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || 'Failed to build graph'
      setError(msg)
      setDone(true)
    } finally {
      setLoading(false)
    }
  }

  // Auto-load when a session becomes available
  useEffect(() => {
    if (currentSessionId && !done) load()
  }, [currentSessionId])

  // Reset zoom to fit — exposed so the header button can call it
  const resetZoom = useCallback(() => {
    if (!svgRef.current || !zoomRef.current) return
    import('d3').then((d3) => {
      const svg = d3.select(svgRef.current as SVGSVGElement)
      svg.transition().duration(400).call(
        zoomRef.current.transform,
        d3.zoomIdentity
      )
    })
  }, [])

  // D3 force simulation — reruns when data or filter changes
  useEffect(() => {
    if (!done || nodes.length === 0 || !svgRef.current) return

    // Stop any previous simulation before starting a new one
    simRef.current?.stop()

    // Abort flag — prevents stale Promise callbacks after cleanup
    let aborted = false
    let timeoutId: ReturnType<typeof setTimeout>

    import('d3').then((d3) => {
      if (aborted || !svgRef.current) return

      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove()

      const W = svgRef.current.clientWidth  || 800
      const H = svgRef.current.clientHeight || 500

      const filteredNodes = filterType === 'all' ? nodes : nodes.filter((n: any) => n.type === filterType)
      const nodeIds       = new Set(filteredNodes.map((n: any) => n.id))
      const filteredEdges = edges.filter((e: any) => nodeIds.has(e.source) && nodeIds.has(e.target))

      const nodesData = filteredNodes.map((n: any) => ({ ...n }))
      const linksData = filteredEdges.map((e: any) => ({ ...e }))

      // Zoom behaviour
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.08, 5])
        .on('zoom', (event) => { g.attr('transform', event.transform) })
      svg.call(zoom)
      zoomRef.current = zoom   // expose for reset button

      const g = svg.append('g')

      // Defs — arrow marker + glow filter
      const defs = svg.append('defs')
      defs.append('marker')
        .attr('id', 'arrow').attr('viewBox', '0 -5 10 10')
        .attr('refX', 18).attr('markerWidth', 6).attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path').attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', 'rgba(255,255,255,0.2)')

      const filter = defs.append('filter').attr('id', 'glow')
      filter.append('feGaussianBlur').attr('stdDeviation', 3).attr('result', 'coloredBlur')
      const feMerge = filter.append('feMerge')
      feMerge.append('feMergeNode').attr('in', 'coloredBlur')
      feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

      // Edges
      const link = g.append('g').selectAll('line')
        .data(linksData).join('line')
        .attr('stroke', 'rgba(255,255,255,0.08)')
        .attr('stroke-width', 1)
        .attr('marker-end', 'url(#arrow)')

      // Nodes
      const node = g.append('g').selectAll<SVGGElement, any>('g')
        .data(nodesData).join('g')
        .style('cursor', 'pointer')
        .on('click', (_event: any, d: any) => setSelected(d))
        .on('mouseenter', function(_event: any, d: any) {
          const color = NODE_COLOR[d.type] || '#64748b'
          d3.select(this).select('circle')
            .transition().duration(150)
            .attr('stroke-width', 3)
            .attr('stroke-opacity', 1)
            .attr('fill-opacity', 1)
            .attr('filter', 'url(#glow)')
          // Highlight connected edges
          link.transition().duration(150)
            .attr('stroke', (l: any) =>
              (l.source?.id ?? l.source) === d.id || (l.target?.id ?? l.target) === d.id
                ? color : 'rgba(255,255,255,0.04)'
            )
            .attr('stroke-width', (l: any) =>
              (l.source?.id ?? l.source) === d.id || (l.target?.id ?? l.target) === d.id ? 1.5 : 0.5
            )
        })
        .on('mouseleave', function() {
          d3.select(this).select('circle')
            .transition().duration(200)
            .attr('stroke-width', 1.5)
            .attr('stroke-opacity', 0.5)
            .attr('fill-opacity', 0.8)
            .attr('filter', null)
          link.transition().duration(200)
            .attr('stroke', 'rgba(255,255,255,0.08)')
            .attr('stroke-width', 1)
        })
        .call(
          d3.drag<SVGGElement, any>()
            .on('start', (event: any, d: any) => {
              if (!event.active) simRef.current?.alphaTarget(0.3).restart()
              d.fx = d.x; d.fy = d.y
            })
            .on('drag',  (event: any, d: any) => { d.fx = event.x; d.fy = event.y })
            .on('end',   (event: any, d: any) => {
              if (!event.active) simRef.current?.alphaTarget(0)
              d.fx = null; d.fy = null
            })
        )

      node.append('circle')
        .attr('r', (d: any) => {
          const deg = linksData.filter((l: any) => l.source === d.id || l.target === d.id).length
          return Math.max(5, Math.min(14, 5 + deg * 1.5))
        })
        .attr('fill',           (d: any) => NODE_COLOR[d.type] || '#64748b')
        .attr('fill-opacity',   0.8)
        .attr('stroke',         (d: any) => NODE_COLOR[d.type] || '#64748b')
        .attr('stroke-width',   1.5)
        .attr('stroke-opacity', 0.5)

      node.append('text')
        .text((d: any) => d.name.length > 16 ? d.name.slice(0, 14) + '…' : d.name)
        .attr('x', 10).attr('y', 4)
        .attr('fill', 'rgba(200,210,230,0.7)')
        .attr('font-size', '9px').attr('font-family', 'monospace')
        .style('pointer-events', 'none')

      const sim = d3.forceSimulation<any>(nodesData)
        .force('link',      d3.forceLink<any, any>(linksData).id((d) => d.id).distance(80).strength(0.5))
        .force('charge',    d3.forceManyBody().strength(-120))
        .force('center',    d3.forceCenter(W / 2, H / 2))
        .force('collision', d3.forceCollide(18))
        .on('tick', () => {
          link
            .attr('x1', (d: any) => d.source.x)
            .attr('y1', (d: any) => d.source.y)
            .attr('x2', (d: any) => d.target.x)
            .attr('y2', (d: any) => d.target.y)
          node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
        })

      simRef.current = sim

      // Zoom to fit after sim settles
      timeoutId = setTimeout(() => {
        if (aborted) return
        const bounds = (g.node() as SVGGElement | null)?.getBBox?.()
        if (bounds && bounds.width > 0 && svgRef.current) {
          const scale = Math.min(0.9, Math.min(W / bounds.width, H / bounds.height) * 0.85)
          const tx = W / 2 - scale * (bounds.x + bounds.width / 2)
          const ty = H / 2 - scale * (bounds.y + bounds.height / 2)
          svg.transition().duration(500).call(
            zoom.transform,
            d3.zoomIdentity.translate(tx, ty).scale(scale)
          )
        }
      }, 1200)
    })

    return () => {
      aborted = true
      clearTimeout(timeoutId)
      simRef.current?.stop()
    }
  }, [done, nodes, edges, filterType])

  // Belt-and-suspenders: stop sim on unmount regardless of filter/data state
  useEffect(() => () => { simRef.current?.stop(); zoomRef.current = null }, [])

  const types = ['all', ...new Set(nodes.map((n: any) => n.type))]

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1 flex-wrap">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Dependency Graph</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'File-level import relationships — drag nodes, scroll to zoom.'
              : 'Scan a repository first to build the graph.'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {done && nodes.length > 0 && (
            <button
              onClick={resetZoom}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all border border-white/[0.08] bg-slate-surface text-slate-500 hover:text-slate-200"
              title="Reset zoom to fit">
              <Maximize2 size={13} /> Reset zoom
            </button>
          )}
          <button
            onClick={load}
            disabled={!currentSessionId || loading}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all disabled:opacity-40',
              done
                ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200'
                : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/30',
            )}
        >
            <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
            {loading ? 'Building…' : done ? 'Rebuild' : 'Build graph'}
          </button>
        </div>
      </div>

      {/* No session */}
      {!currentSessionId && (
        <div className={`${CARD} p-10 text-center`}>
          <Terminal size={24} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-500 text-[14px] font-medium">No active scan session</p>
          <Link to="/scanner"
            className="mt-3 inline-block text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
            Go to Scanner →
          </Link>
        </div>
      )}

      {/* Loading */}
      {currentSessionId && loading && (
        <div className={`${CARD} p-10 text-center`}>
          <GitBranch size={22} className="text-indigo-400/60 animate-pulse mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Mapping import relationships…</p>
        </div>
      )}

      {/* Error */}
      {done && !loading && error && (
        <div className={`${CARD} p-8 text-center`}>
          <AlertTriangle size={22} className="text-amber-400 mx-auto mb-3" />
          <p className="text-slate-400 text-[13px] mb-1">Failed to build graph</p>
          <p className="text-slate-600 text-[11px] font-mono">{error}</p>
          <button onClick={load}
            className="mt-4 text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
            Retry
          </button>
        </div>
      )}

      {/* Graph */}
      {done && !loading && !error && nodes.length > 0 && (
        <>
          <div className="flex items-center gap-4 flex-wrap">
            <div className={`${CARD} px-5 py-3 flex items-center gap-6`}>
              <div className="text-center">
                <p className="text-[22px] font-black text-white font-tight">{stats?.files ?? nodes.length}</p>
                <p className="text-[10px] text-slate-600 uppercase tracking-wider">Files</p>
              </div>
              <div className="w-px h-8 bg-white/[0.06]" />
              <div className="text-center">
                <p className="text-[22px] font-black text-white font-tight">{stats?.imports ?? edges.length}</p>
                <p className="text-[10px] text-slate-600 uppercase tracking-wider">Imports</p>
              </div>
              <div className="w-px h-8 bg-white/[0.06]" />
              {Object.entries(NODE_COLOR).map(([type, color]) => (
                <div key={type} className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-[10px] text-slate-500 capitalize">{type}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              {types.map(t => (
                <button key={t} type="button" onClick={() => setFilterType(t)}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-[10px] font-semibold capitalize transition-all border',
                    filterType === t
                      ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
                      : 'border-white/[0.07] text-slate-600 hover:text-slate-400',
                  )}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className={`${CARD} overflow-hidden relative`} style={{ height: 520 }}>
            <svg ref={svgRef} width="100%" height="100%" style={{ background: 'transparent' }} />
            {selected && (
              <div className="absolute bottom-4 left-4 right-4 max-w-sm">
                <div className={`${CARD} px-4 py-3 flex items-start justify-between gap-3`}>
                  <div className="min-w-0">
                    <p className="text-[12px] font-semibold text-slate-200 font-mono truncate">{selected.name}</p>
                    <p className="text-[10px] text-slate-600 font-mono truncate mt-0.5">{selected.path}</p>
                    <span className="text-[9px] px-1.5 py-0.5 rounded capitalize font-medium mt-1 inline-block"
                      style={{ color: NODE_COLOR[selected.type], backgroundColor: `${NODE_COLOR[selected.type]}18` }}>
                      {selected.type}
                    </span>
                  </div>
                  <button onClick={() => setSelected(null)}
                    className="text-slate-700 hover:text-slate-400 text-[10px] shrink-0 mt-0.5">✕</button>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Empty */}
      {done && !loading && !error && nodes.length === 0 && (
        <div className={`${CARD} p-10 text-center`}>
          <GitBranch size={24} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-400 text-[14px] font-medium">No import relationships found</p>
          <p className="text-slate-600 text-[12px] mt-1">Run a full scan first to map the codebase structure.</p>
          <Link to="/scanner"
            className="mt-3 inline-block text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
            Go to Scanner →
          </Link>
        </div>
      )}
    </div>
  )
}
