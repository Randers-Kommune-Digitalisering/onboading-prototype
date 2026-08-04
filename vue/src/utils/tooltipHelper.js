const TOOLTIP_SNAPSHOT_ATTR = 'data-tooltip-js-snapshot'

const clamp = (value, min, max) => Math.min(max, Math.max(min, value))

const snapshotInlineStyles = (el) => {
    if (el.hasAttribute(TOOLTIP_SNAPSHOT_ATTR)) return

    const snapshot = {
        position: el.style.position,
        left: el.style.left,
        top: el.style.top,
        right: el.style.right,
        bottom: el.style.bottom,
        transform: el.style.transform,
        margin: el.style.margin,
        zIndex: el.style.zIndex,
        display: el.style.display,
        visibility: el.style.visibility,
        maxWidth: el.style.maxWidth,
        whiteSpace: el.style.whiteSpace,
        overflowWrap: el.style.overflowWrap,
        wordBreak: el.style.wordBreak,
    }

    el.setAttribute(TOOLTIP_SNAPSHOT_ATTR, JSON.stringify(snapshot))
}

const restoreInlineStyles = (el) => {
    const raw = el.getAttribute(TOOLTIP_SNAPSHOT_ATTR)
    if (!raw) return

    let snapshot
    try {
        snapshot = JSON.parse(raw)
    } catch {
        el.removeAttribute(TOOLTIP_SNAPSHOT_ATTR)
        return
    }

    el.style.position = snapshot.position
    el.style.left = snapshot.left
    el.style.top = snapshot.top
    el.style.right = snapshot.right
    el.style.bottom = snapshot.bottom
    el.style.transform = snapshot.transform
    el.style.margin = snapshot.margin
    el.style.zIndex = snapshot.zIndex
    el.style.display = snapshot.display
    el.style.visibility = snapshot.visibility
    el.style.maxWidth = snapshot.maxWidth
    el.style.whiteSpace = snapshot.whiteSpace
    el.style.overflowWrap = snapshot.overflowWrap
    el.style.wordBreak = snapshot.wordBreak

    el.removeAttribute(TOOLTIP_SNAPSHOT_ATTR)
}

const getTooltipEl = (hoverEl) => {
    if (!hoverEl) return null

    // Prefer direct child tooltip, but fall back to any descendant.
    // `:scope` isn't universally supported, so keep it defensive.
    try {
        return hoverEl.querySelector(':scope > .tooltip-display') || hoverEl.querySelector('.tooltip-display')
    } catch {
        return hoverEl.querySelector('.tooltip-display')
    }
}

const positionTooltip = ({ hoverEl, tooltipEl }) => {
    if (!hoverEl || !tooltipEl) return

    // Ensure we can measure it (CSS uses display:none until :hover)
    tooltipEl.style.display = 'block'
    tooltipEl.style.visibility = 'hidden'

    // Use viewport positioning so it won't be clipped by overflow containers
    tooltipEl.style.position = 'fixed'
    tooltipEl.style.left = '0px'
    tooltipEl.style.top = '0px'
    tooltipEl.style.right = ''
    tooltipEl.style.bottom = ''
    tooltipEl.style.transform = 'none'
    tooltipEl.style.margin = '0'
    tooltipEl.style.zIndex = '1000'

    const padding = 12
    const offset = 8
    const viewportW = window.innerWidth
    const viewportH = window.innerHeight
    const maxW = Math.min(384, viewportW - padding * 2)

    tooltipEl.style.maxWidth = `${maxW}px`

    // Measure after the style changes
    const triggerRect = hoverEl.getBoundingClientRect()
    let tooltipRect = tooltipEl.getBoundingClientRect()

    // If constrained, allow wrapping to reduce overflow (e.g. long URLs)
    if (tooltipRect.width > maxW) {
        tooltipEl.style.whiteSpace = 'normal'
        tooltipEl.style.overflowWrap = 'anywhere'
        tooltipEl.style.wordBreak = 'break-word'
        tooltipRect = tooltipEl.getBoundingClientRect()
    }

    // Center above trigger by default
    let left = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
    left = clamp(left, padding, viewportW - padding - tooltipRect.width)

    let top = triggerRect.top - tooltipRect.height - offset

    // If it would go above the viewport, flip below
    if (top < padding) {
        top = triggerRect.bottom + offset
    }

    // Last resort: clamp vertically too
    top = clamp(top, padding, viewportH - padding - tooltipRect.height)

    tooltipEl.style.left = `${Math.round(left)}px`
    tooltipEl.style.top = `${Math.round(top)}px`
    tooltipEl.style.visibility = 'visible'
}

export const installTooltipHelper = () => {
    const state = {
        activeHoverEl: null,
        activeTooltipEl: null,
        raf: 0,
        domUpdateRaf: 0,
        observer: null,
    }

    const disconnectObserver = () => {
        if (state.observer) {
            state.observer.disconnect()
            state.observer = null
        }
    }

    const deactivateTooltip = () => {
        if (state.activeTooltipEl) {
            restoreInlineStyles(state.activeTooltipEl)
        }
        state.activeHoverEl = null
        state.activeTooltipEl = null
        cancelAnimationFrame(state.raf)
        cancelAnimationFrame(state.domUpdateRaf)
        disconnectObserver()
    }

    const scheduleTooltipPositionAfterDomUpdate = () => {
        // Vue typically updates DOM after the event handler; double-rAF waits
        // for layout to settle so our measurements are correct.
        cancelAnimationFrame(state.domUpdateRaf)
        state.domUpdateRaf = requestAnimationFrame(() => {
            state.domUpdateRaf = requestAnimationFrame(() => {
                scheduleTooltipPosition()
            })
        })
    }

    const scheduleTooltipPosition = () => {
        if (!state.activeHoverEl || !state.activeTooltipEl) return

        if (!state.activeHoverEl.isConnected || !state.activeTooltipEl.isConnected) {
            deactivateTooltip()
            return
        }

        if (!state.activeHoverEl.matches(':hover')) {
            deactivateTooltip()
            return
        }

        // Tooltip element can be swapped (e.g. v-if) while hovered.
        // Re-acquire it so positioning applies to the currently rendered tooltip.
        const currentTooltipEl = getTooltipEl(state.activeHoverEl)
        if (!currentTooltipEl) {
            deactivateTooltip()
            return
        }
        if (currentTooltipEl !== state.activeTooltipEl) {
            restoreInlineStyles(state.activeTooltipEl)
            state.activeTooltipEl = currentTooltipEl
            snapshotInlineStyles(state.activeTooltipEl)
        }

        cancelAnimationFrame(state.raf)
        state.raf = requestAnimationFrame(() => {
            positionTooltip({ hoverEl: state.activeHoverEl, tooltipEl: state.activeTooltipEl })
        })
    }

    const startObserver = (hoverEl) => {
        disconnectObserver()
        if (!hoverEl) return

        state.observer = new MutationObserver(() => {
            if (!state.activeHoverEl) return
            scheduleTooltipPositionAfterDomUpdate()
        })

        state.observer.observe(hoverEl, {
            subtree: true,
            childList: true,
            characterData: true,
        })
    }

    const activateTooltip = (hoverEl) => {
        const tooltipEl = getTooltipEl(hoverEl)
        if (!tooltipEl) return

        if (state.activeTooltipEl && state.activeTooltipEl !== tooltipEl) {
            restoreInlineStyles(state.activeTooltipEl)
        }

        state.activeHoverEl = hoverEl
        state.activeTooltipEl = tooltipEl

        snapshotInlineStyles(tooltipEl)
        startObserver(hoverEl)
        scheduleTooltipPosition()
    }

    const onTooltipPointerOver = (e) => {
        const hoverEl = e.target?.closest?.('.tooltip-hover')
        if (!hoverEl) return

        if (state.activeHoverEl === hoverEl) {
            scheduleTooltipPosition()
            return
        }

        activateTooltip(hoverEl)
    }

    const onTooltipPointerOut = (e) => {
        if (!state.activeHoverEl) return

        const leavingHoverEl = e.target?.closest?.('.tooltip-hover')
        if (leavingHoverEl !== state.activeHoverEl) return

        const nextTarget = e.relatedTarget
        if (nextTarget && state.activeHoverEl.contains(nextTarget)) return

        deactivateTooltip()
    }

    const onDocumentClick = (e) => {
        if (!state.activeHoverEl) return
        if (!state.activeHoverEl.contains(e.target)) return
        scheduleTooltipPositionAfterDomUpdate()
    }

    document.addEventListener('pointerover', onTooltipPointerOver, true)
    document.addEventListener('pointerout', onTooltipPointerOut, true)
    document.addEventListener('click', onDocumentClick, true)
    window.addEventListener('scroll', scheduleTooltipPosition, true)
    window.addEventListener('resize', scheduleTooltipPosition)

    return () => {
        document.removeEventListener('pointerover', onTooltipPointerOver, true)
        document.removeEventListener('pointerout', onTooltipPointerOut, true)
        document.removeEventListener('click', onDocumentClick, true)
        window.removeEventListener('scroll', scheduleTooltipPosition, true)
        window.removeEventListener('resize', scheduleTooltipPosition)
        deactivateTooltip()
    }
}
