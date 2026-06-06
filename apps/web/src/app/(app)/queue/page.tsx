import { JobDataTable } from "@/components/jobs/job-data-table";
import { JobKanban } from "@/components/jobs/job-kanban";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function QueuePage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <Tabs defaultValue="table">
        <TabsList>
          <TabsTrigger value="table">Table</TabsTrigger>
          <TabsTrigger value="board">Board</TabsTrigger>
        </TabsList>
        <TabsContent value="table" className="mt-4">
          <JobDataTable />
        </TabsContent>
        <TabsContent value="board" className="mt-4">
          <JobKanban />
        </TabsContent>
      </Tabs>
    </div>
  );
}
