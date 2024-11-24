import {
  Button,
  Container,
  Flex,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { ChatMessagesService } from "../../client"

import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"

import AddChatMessage from "../../components/ChatMessages/AddChatMessage"

const chatMessagesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/chatMessages")({
  component: ChatMessages,
  validateSearch: (search) => chatMessagesSearchSchema.parse(search),
})

const PER_PAGE = 5

function getChatMessagesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ChatMessagesService.readChatMessages({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["chatMessages", { page }],
  }
}

function ChatMessagesTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev) => ({ ...prev, page }) })

  const {
    data: chatMessages,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getChatMessagesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && chatMessages?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getChatMessagesQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Message</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {chatMessages?.data.map((chatMessage) => (
                <Tr key={chatMessage.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{chatMessage.id}</Td>
                  <Td isTruncated maxWidth="150px">
                    {chatMessage.message}
                  </Td>
                  <Td>
                    <ActionsMenu type={"ChatMessage"} value={chatMessage} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <Flex
        gap={4}
        alignItems="center"
        mt={4}
        direction="row"
        justifyContent="flex-end"
      >
        <Button onClick={() => setPage(page - 1)} isDisabled={!hasPreviousPage}>
          Previous
        </Button>
        <span>Page {page}</span>
        <Button isDisabled={!hasNextPage} onClick={() => setPage(page + 1)}>
          Next
        </Button>
      </Flex>
    </>
  )
}

function ChatMessages() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        ChatMessages Management
      </Heading>

      <Navbar type={"ChatMessage"} addModalAs={AddChatMessage} />
      <ChatMessagesTable />
    </Container>
  )
}
