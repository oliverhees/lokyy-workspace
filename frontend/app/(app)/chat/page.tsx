// F2 — Chat now lives inside the app shell (sidebar + top bar come from the
// (app) layout). The page only supplies its content.
import { Chat } from "@/components/chat/Chat";

export default function ChatPage() {
  return (
    <div className="flex h-full flex-col">
      <Chat />
    </div>
  );
}
