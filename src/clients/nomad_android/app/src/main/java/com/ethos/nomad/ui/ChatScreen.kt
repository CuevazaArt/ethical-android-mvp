// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch

// ── Main Chat Screen ─────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(viewModel: ChatViewModel = viewModel()) {
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    val messageCount = viewModel.messages.size
    val isThinking = viewModel.isThinking.value
    val streamingText = viewModel.streamingText.value
    val isConnected = viewModel.isConnected.value
    val metadata = viewModel.currentMetadata.value
    val vaultKey = viewModel.pendingVaultKey.value
    val isSpeaking = viewModel.isSpeaking.value

    // Auto-scroll when new messages arrive or streaming updates
    LaunchedEffect(messageCount, streamingText) {
        if (messageCount > 0) {
            listState.animateScrollToItem(messageCount - 1)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EthosColors.BgPrimary)
    ) {
        // ── Top Bar ──────────────────────────────────────────
        TopBar(isConnected = isConnected, metadata = metadata, isSpeaking = isSpeaking)

        // ── Messages List ────────────────────────────────────
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 12.dp),
            state = listState,
            verticalArrangement = Arrangement.spacedBy(6.dp),
            contentPadding = PaddingValues(vertical = 8.dp)
        ) {
            // Welcome message
            if (viewModel.messages.isEmpty() && !isThinking) {
                item {
                    WelcomeCard()
                }
            }

            items(viewModel.messages) { message ->
                ChatBubble(message)
            }

            // Streaming indicator
            if (isThinking || streamingText.isNotEmpty()) {
                item {
                    StreamingBubble(text = streamingText, isThinking = isThinking)
                }
            }
        }

        // ── Input Bar ────────────────────────────────────────
        InputBar(
            text = inputText,
            onTextChange = { inputText = it },
            onSend = {
                if (inputText.isNotBlank()) {
                    viewModel.sendMessage(inputText)
                    inputText = ""
                    coroutineScope.launch {
                        listState.animateScrollToItem(viewModel.messages.size)
                    }
                }
            },
            enabled = isConnected
        )
    }

    // Vault authorization dialog
    if (vaultKey != null) {
        VaultAuthDialog(
            keyName = vaultKey,
            onApprove = { viewModel.approveVault(vaultKey) },
            onDeny = { viewModel.denyVault() }
        )
    }
}

// ── Top Bar ──────────────────────────────────────────────────────

@Composable
private fun TopBar(isConnected: Boolean, metadata: EthicsMetadata, isSpeaking: Boolean = false) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(EthosColors.BgSurface)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Connection dot
        Box(
            modifier = Modifier
                .size(10.dp)
                .clip(CircleShape)
                .background(if (isConnected) EthosColors.AccentGreen else EthosColors.AccentRed)
        )
        Spacer(modifier = Modifier.width(10.dp))

        Text(
            text = "Ethos Kernel",
            color = EthosColors.TextPrimary,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.weight(1f)
        )

        // TTS speaking indicator
        if (isSpeaking) {
            val speakAlpha by rememberInfiniteTransition(label = "speak").animateFloat(
                initialValue = 0.4f,
                targetValue = 1.0f,
                animationSpec = infiniteRepeatable(
                    animation = tween(500, easing = FastOutSlowInEasing),
                    repeatMode = RepeatMode.Reverse
                ),
                label = "speakAlpha"
            )
            Icon(
                Icons.Default.VolumeUp,
                contentDescription = "Hablando",
                tint = EthosColors.AccentGreen.copy(alpha = speakAlpha),
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
        }

        // Ethics context badge
        if (metadata.context.isNotEmpty() && metadata.context != "everyday_ethics") {
            Surface(
                color = when {
                    metadata.risk > 0.5f -> EthosColors.AccentRed.copy(alpha = 0.2f)
                    metadata.urgency > 0.5f -> EthosColors.AccentGold.copy(alpha = 0.2f)
                    else -> EthosColors.AccentBlue.copy(alpha = 0.15f)
                },
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    text = metadata.context.replace("_", " "),
                    color = when {
                        metadata.risk > 0.5f -> EthosColors.AccentRed
                        metadata.urgency > 0.5f -> EthosColors.AccentGold
                        else -> EthosColors.AccentBlue
                    },
                    fontSize = 10.sp,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
    }

    // Thin accent line under top bar
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(
                Brush.horizontalGradient(
                    listOf(
                        EthosColors.AccentGreen.copy(alpha = 0.0f),
                        EthosColors.AccentGreen.copy(alpha = 0.6f),
                        EthosColors.AccentBlue.copy(alpha = 0.6f),
                        EthosColors.AccentBlue.copy(alpha = 0.0f)
                    )
                )
            )
    )
}

// ── Welcome Card ─────────────────────────────────────────────────

@Composable
private fun WelcomeCard() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "⬡",
            fontSize = 48.sp,
            color = EthosColors.AccentGreen,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = "Ethos Kernel",
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
            color = EthosColors.TextPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "Percepción ética · Memoria narrativa · Identidad reflexiva",
            fontSize = 12.sp,
            color = EthosColors.TextSecondary,
            textAlign = TextAlign.Center
        )
    }
}

// ── Chat Bubble ──────────────────────────────────────────────────

@Composable
fun ChatBubble(message: ChatMessage) {
    val isUser = message.isUser
    val alignment = if (isUser) Alignment.CenterEnd else Alignment.CenterStart

    val bubbleColor = when {
        message.isBlocked -> EthosColors.BubbleBlocked
        isUser -> EthosColors.BubbleUser
        else -> EthosColors.BubbleEthos
    }

    val borderColor = when {
        message.isBlocked -> EthosColors.AccentRed.copy(alpha = 0.5f)
        isUser -> Color.Transparent
        else -> EthosColors.AccentGreen.copy(alpha = 0.15f)
    }

    val shape = RoundedCornerShape(
        topStart = 14.dp,
        topEnd = 14.dp,
        bottomStart = if (isUser) 14.dp else 4.dp,
        bottomEnd = if (isUser) 4.dp else 14.dp
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp),
        contentAlignment = alignment
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .border(1.dp, borderColor, shape)
                .clip(shape)
                .background(bubbleColor)
                .padding(12.dp)
        ) {
            // Blocked warning
            if (message.isBlocked) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = EthosColors.AccentRed,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Bloqueado por seguridad",
                        color = EthosColors.AccentRed,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
            }

            // Message text
            Text(
                text = message.text,
                color = EthosColors.TextPrimary,
                fontSize = 14.sp,
                lineHeight = 20.sp
            )

            // Footer metadata
            if (!isUser && (message.latencyMs != null || message.pluginUsed != null)) {
                Spacer(modifier = Modifier.height(6.dp))
                Row {
                    if (message.latencyMs != null) {
                        Text(
                            text = "${message.latencyMs}ms",
                            color = EthosColors.TextMuted,
                            fontSize = 10.sp
                        )
                    }
                    if (message.pluginUsed != null) {
                        if (message.latencyMs != null) {
                            Text(text = " · ", color = EthosColors.TextMuted, fontSize = 10.sp)
                        }
                        Text(
                            text = "🔌 ${message.pluginUsed}",
                            color = EthosColors.AccentGreen,
                            fontSize = 10.sp
                        )
                    }
                }
            }
        }
    }
}

// ── Streaming Bubble (Ethos is typing...) ────────────────────────

@Composable
private fun StreamingBubble(text: String, isThinking: Boolean) {
    val pulseAlpha by rememberInfiniteTransition(label = "pulse").animateFloat(
        initialValue = 0.3f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp),
        contentAlignment = Alignment.CenterStart
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .border(
                    1.dp,
                    EthosColors.AccentGreen.copy(alpha = 0.25f),
                    RoundedCornerShape(14.dp, 14.dp, 14.dp, 4.dp)
                )
                .clip(RoundedCornerShape(14.dp, 14.dp, 14.dp, 4.dp))
                .background(EthosColors.BubbleEthos)
                .padding(12.dp)
        ) {
            if (text.isNotEmpty()) {
                Text(
                    text = text,
                    color = EthosColors.TextPrimary,
                    fontSize = 14.sp,
                    lineHeight = 20.sp
                )
                Spacer(modifier = Modifier.height(4.dp))
            }

            AnimatedVisibility(visible = isThinking, enter = fadeIn(), exit = fadeOut()) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "●",
                        color = EthosColors.AccentGreen.copy(alpha = pulseAlpha),
                        fontSize = 8.sp
                    )
                    Spacer(modifier = Modifier.width(3.dp))
                    Text(
                        text = if (text.isEmpty()) "Ethos está pensando..." else "generando...",
                        color = EthosColors.TextSecondary.copy(alpha = pulseAlpha),
                        fontSize = 11.sp
                    )
                }
            }
        }
    }
}

// ── Input Bar ────────────────────────────────────────────────────

@Composable
private fun InputBar(
    text: String,
    onTextChange: (String) -> Unit,
    onSend: () -> Unit,
    enabled: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(EthosColors.BgSurface)
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = text,
            onValueChange = onTextChange,
            modifier = Modifier.weight(1f),
            placeholder = {
                Text(
                    text = if (enabled) "Escribe a Ethos..." else "Conectando...",
                    color = EthosColors.TextMuted
                )
            },
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = EthosColors.TextPrimary,
                unfocusedTextColor = EthosColors.TextPrimary,
                cursorColor = EthosColors.AccentGreen,
                focusedBorderColor = EthosColors.AccentGreen.copy(alpha = 0.5f),
                unfocusedBorderColor = EthosColors.Border,
                focusedContainerColor = EthosColors.BgInput,
                unfocusedContainerColor = EthosColors.BgInput
            ),
            shape = RoundedCornerShape(20.dp),
            singleLine = true,
            enabled = enabled,
            keyboardOptions = KeyboardOptions.Default.copy(imeAction = ImeAction.Send),
            keyboardActions = KeyboardActions(onSend = { onSend() })
        )

        Spacer(modifier = Modifier.width(8.dp))

        IconButton(
            onClick = onSend,
            enabled = enabled && text.isNotBlank(),
            modifier = Modifier
                .size(44.dp)
                .clip(CircleShape)
                .background(
                    if (enabled && text.isNotBlank())
                        EthosColors.AccentGreen
                    else
                        EthosColors.Border
                )
        ) {
            Icon(
                Icons.Default.Send,
                contentDescription = "Enviar",
                tint = if (enabled && text.isNotBlank())
                    EthosColors.BgPrimary
                else
                    EthosColors.TextMuted,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

// ── Vault Authorization Dialog ───────────────────────────────────

@Composable
private fun VaultAuthDialog(
    keyName: String,
    onApprove: () -> Unit,
    onDeny: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDeny,
        icon = {
            Icon(
                Icons.Default.Lock,
                contentDescription = null,
                tint = EthosColors.AccentGold,
                modifier = Modifier.size(32.dp)
            )
        },
        title = {
            Text(
                text = "Autorización de Bóveda",
                color = EthosColors.TextPrimary,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Text(
                text = "Ethos solicita acceso a la llave protegida:\n\n\"$keyName\"\n\n¿Autorizas el acceso?",
                color = EthosColors.TextSecondary,
                lineHeight = 20.sp
            )
        },
        confirmButton = {
            TextButton(onClick = onApprove) {
                Text("Autorizar", color = EthosColors.AccentGreen, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDeny) {
                Text("Denegar", color = EthosColors.AccentRed)
            }
        },
        containerColor = EthosColors.BgSurface,
        tonalElevation = 0.dp
    )
}
