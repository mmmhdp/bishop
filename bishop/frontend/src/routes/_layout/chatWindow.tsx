import {
  Container,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import { z } from "zod"

const chatWindowSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/chatWindow")({
  component: ChatWindowPage,
  validateSearch: (search) => chatWindowSearchSchema.parse(search),
});

function ChatWindowPage() {
  return (
    <Container maxW="full">
      <ChatWindow />
    </Container>
  );
}

