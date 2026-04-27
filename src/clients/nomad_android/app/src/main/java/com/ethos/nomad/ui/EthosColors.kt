// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.ui

import androidx.compose.ui.graphics.Color

/**
 * EthosColors — Design system for the Nomad Android App.
 * Dark cyberpunk palette matching the Ethos Kernel dashboard.
 */
object EthosColors {
    val BgPrimary     = Color(0xFF0D1117)
    val BgSurface     = Color(0xFF161B22)
    val BgInput       = Color(0xFF1C2128)
    val Border        = Color(0xFF21262D)
    val BorderFocus   = Color(0xFF388BFD)

    val AccentGreen   = Color(0xFF3FB950)
    val AccentBlue    = Color(0xFF58A6FF)
    val AccentGold    = Color(0xFFD29922)
    val AccentRed     = Color(0xFFF85149)

    val TextPrimary   = Color(0xFFE6EDF3)
    val TextSecondary = Color(0xFF8B949E)
    val TextMuted     = Color(0xFF484F58)

    // Bubble-specific
    val BubbleUser    = Color(0xFF1F3A5F)  // Deep blue tint
    val BubbleEthos   = Color(0xFF1A2332)  // Dark surface with green accent
    val BubbleBlocked = Color(0xFF3D1518)  // Dark red tint for safety blocks
}
