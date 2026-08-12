<script setup lang="ts">
import { nextTick, onMounted, ref } from "vue";
import { Dumbbell, MessageSquarePlus, PanelLeft, Send, User, X } from "@lucide/vue";
import api from "../api/api";

type ChatMessage = { role: "user" | "coach"; content: string };
type ApiChatMessage = { role: "user" | "assistant"; content: string; created_at: string };
type ChatThread = { id: string; title: string; updated_at: string };

const introMessage: ChatMessage = {
  role: "coach",
  content: "Hi! I’m your FitCoach. I can use your program, workout history, and preferences to help you train.",
};

const message = ref("");
const isSending = ref(false);
const isLoadingChats = ref(true);
const isLoadingMessages = ref(false);
const error = ref("");
const composer = ref<HTMLTextAreaElement | null>(null);
const messagePane = ref<HTMLDivElement | null>(null);
const activeChatId = ref<string | null>(null);
const isSidebarOpen = ref(true);
const threads = ref<ChatThread[]>([]);
const messages = ref<ChatMessage[]>([introMessage]);

const COULD_NOT_LOAD_CHAT = "We couldn’t load that chat. Please try again.";
const COULD_NOT_LOAD_HISTORY = "Your coach history could not be loaded. Please try again.";
const COULD_NOT_REPLY = "Your coach could not respond. Please try again.";

function resizeComposer() {
  if (!composer.value) return;
  composer.value.style.height = "0px";
  composer.value.style.height = `${Math.min(composer.value.scrollHeight, 160)}px`;
}

async function scrollToBottom(behavior: ScrollBehavior = "smooth") {
  await nextTick();
  messagePane.value?.scrollTo({ top: messagePane.value.scrollHeight, behavior });
}

function setDraftChat() {
  activeChatId.value = null;
  messages.value = [introMessage];
  error.value = "";
  if (window.innerWidth < 1024) {
    isSidebarOpen.value = false;
  }
  void scrollToBottom("auto");
}

function mapChatMessage(item: ApiChatMessage): ChatMessage {
  return {
    role: item.role === "user" ? "user" : "coach",
    content: item.content,
  };
}

function formatChatDate(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(parsed);
}

function handleComposerKeydown(event: KeyboardEvent) {
  if (event.key !== "Enter" || event.shiftKey) return;
  event.preventDefault();
  void send();
}

async function fetchChats() {
  const { data } = await api.get<{ chats: ChatThread[] }>("/coach/chats");
  threads.value = data.chats;
}

async function loadChat(chatId: string) {
  activeChatId.value = chatId;
  isLoadingMessages.value = true;
  error.value = "";
  try {
    const { data } = await api.get<{ messages: ApiChatMessage[] }>(`/coach/chats/${chatId}`);
    messages.value = data.messages.map(mapChatMessage);
    if (window.innerWidth < 1024) {
      isSidebarOpen.value = false;
    }
    void scrollToBottom("auto");
  } catch {
    error.value = COULD_NOT_LOAD_CHAT;
  } finally {
    isLoadingMessages.value = false;
  }
}

async function loadInitialState() {
  isLoadingChats.value = true;
  error.value = "";
  isSidebarOpen.value = window.innerWidth >= 1024;
  try {
    await fetchChats();
    const firstThread = threads.value[0];
    if (firstThread) {
      await loadChat(firstThread.id);
    } else {
      setDraftChat();
    }
  } catch {
    error.value = COULD_NOT_LOAD_HISTORY;
    setDraftChat();
  } finally {
    isLoadingChats.value = false;
  }
}

async function send() {
  const content = message.value.trim();
  if (!content || isSending.value) return;

  const currentChatId = activeChatId.value;
  messages.value.push({ role: "user", content });
  message.value = "";
  error.value = "";
  isSending.value = true;
  await nextTick();
  resizeComposer();
  await scrollToBottom();

  try {
    const { data } = await api.post<{ reply: string; thread_id: string }>("/coach/chat", {
      message: content,
      thread_id: currentChatId,
    });
    messages.value.push({ role: "coach", content: data.reply });
    if (!currentChatId) {
      activeChatId.value = data.thread_id;
    }
    await fetchChats();
  } catch {
    error.value = COULD_NOT_REPLY;
  } finally {
    isSending.value = false;
    await nextTick();
    resizeComposer();
    await scrollToBottom();
  }
}

onMounted(() => {
  void loadInitialState();
});
</script>

<template>
  <main class="flex h-[calc(100vh-65px)] bg-white">
    <div v-if="isSidebarOpen" class="fixed inset-0 z-10 bg-slate-900/30 lg:hidden" @click="isSidebarOpen = false" />

    <!-- Sidebar -->
    <aside
      :class="isSidebarOpen ? 'w-[280px] translate-x-0' : 'w-0 -translate-x-full lg:w-0'"
      class="fixed inset-y-0 left-0 z-20 flex shrink-0 flex-col overflow-hidden border-r border-slate-200 bg-slate-50 transition-all duration-200 lg:static lg:h-full"
    >
      <div class="flex h-full w-[280px] flex-col">
        <div class="flex items-center justify-between px-4 py-4">
          <div class="flex items-center gap-2">
          </div>
          <button
            class="grid size-8 place-items-center rounded-lg text-slate-500 transition hover:bg-slate-200 hover:text-slate-900 lg:hidden"
            type="button"
            aria-label="Close sidebar"
            @click="isSidebarOpen = false"
          >
            <X :size="16" />
          </button>
        </div>

        <div class="px-3 pb-3">
          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            type="button"
            @click="setDraftChat"
          >
            <MessageSquarePlus :size="16" />
            New chat
          </button>
        </div>

        <nav class="flex-1 space-y-0.5 overflow-y-auto px-2 pb-3" aria-label="Chat history">
          <p v-if="isLoadingChats" class="px-2 py-3 text-xs text-slate-400">Loading chats…</p>
          <p v-else-if="!threads.length" class="px-2 py-3 text-xs text-slate-400">No saved chats yet.</p>

          <button
            v-for="thread in threads"
            :key="thread.id"
            :class="activeChatId === thread.id ? 'bg-blue-100 text-blue-900' : 'text-slate-600 hover:bg-slate-200/70'"
            class="block w-full truncate rounded-lg px-3 py-2 text-left text-sm transition"
            type="button"
            @click="loadChat(thread.id)"
          >
            {{ thread.title }}
            <span class="ml-1 text-xs text-slate-400">· {{ formatChatDate(thread.updated_at) }}</span>
          </button>
        </nav>
      </div>
    </aside>

    <!-- Chat pane -->
    <section class="flex min-w-0 flex-1 flex-col">
      <header class="flex shrink-0 items-center gap-3 border-b border-slate-200 px-4 py-3 sm:px-6">
        <button
          class="grid size-9 shrink-0 place-items-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
          type="button"
          aria-label="Toggle sidebar"
          @click="isSidebarOpen = !isSidebarOpen"
        >
          <PanelLeft :size="18" />
        </button>
        <h2 class="truncate text-sm font-medium text-slate-900">
          {{ activeChatId ? threads.find((thread) => thread.id === activeChatId)?.title ?? "Chat" : "New chat" }}
        </h2>
      </header>

      <div ref="messagePane" class="flex-1 overflow-y-auto" aria-live="polite">
        <div class="mx-auto max-w-3xl px-4 py-6 sm:px-6">
          <p v-if="isLoadingMessages" class="text-sm text-slate-500">Loading messages…</p>

          <div v-else class="space-y-6">
            <div v-for="(item, index) in messages" :key="index" class="flex items-start gap-3" :class="item.role === 'user' ? 'flex-row-reverse' : ''">
              <div
                class="grid size-8 shrink-0 place-items-center rounded-full"
                :class="item.role === 'user' ? 'bg-slate-200 text-slate-600' : ' bg-blue-600 text-white'"
              >
                <User v-if="item.role === 'user'" :size="15" />
                <Dumbbell v-else :size="15" />
              </div>
              <div
                class="max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-6 sm:max-w-[75%]"
                :class="item.role === 'user' ? ' bg-blue-600 text-white' : 'bg-slate-100 text-slate-800'"
              >
                {{ item.content }}
              </div>
            </div>

            <div v-if="isSending" class="flex items-start gap-3">
              <div class="grid size-8 shrink-0 place-items-center rounded-full bg-blue-600 text-white">
                <Dumbbell :size="15" />
              </div>
              <div class="flex items-center gap-1 rounded-2xl bg-slate-100 px-4 py-3">
                <span class="size-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:0ms]" />
                <span class="size-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:150ms]" />
                <span class="size-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:300ms]" />
              </div>
            </div>
          </div>

          <p v-if="error" class="mt-4 text-sm text-rose-600">{{ error }}</p>
        </div>
      </div>

      <form class="shrink-0 border-t border-slate-200 p-4 sm:p-5" @submit.prevent="send">
        <div class="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-slate-200 bg-white p-1.5 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">
          <textarea
            ref="composer"
            v-model="message"
            :disabled="isSending"
            rows="1"
            class="max-h-40 min-h-[44px] min-w-0 flex-1 resize-none bg-transparent px-3 py-2 text-sm leading-6 outline-none disabled:cursor-not-allowed"
            placeholder="Ask your coach anything..."
            @input="resizeComposer"
            @keydown="handleComposerKeydown"
          />
          <button
            :disabled="isSending || !message.trim()"
            class="grid size-10 shrink-0 place-items-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Send message"
            type="submit"
          >
            <Send :size="16" />
          </button>
        </div>
      </form>
    </section>
  </main>
</template>
