import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

interface AcquisitionHistoryCardProps {
  id: number;
  fileName: string;
  numDataPoints: number;
  startTime: string;
  endTime: string;
  sensorType: string;
  status: string;
  locationId: number;
}

export function AcquisitionHistoryCard({
  id,
  fileName,
  numDataPoints,
  startTime,
  endTime,
  sensorType,
  status,
  locationId,
}: AcquisitionHistoryCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "failed":
        return "bg-red-500";
      case "in_progress":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <Link href={`/locations/${locationId}/acquisitions/${id}`}>
      <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            {fileName || `Acquisition ${id}`}
          </CardTitle>
          <Badge className={getStatusColor(status)}>
            {status.replace("_", " ")}
          </Badge>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground space-y-1">
            <p>Sensor Type: {sensorType}</p>
            <p>Data Points: {numDataPoints}</p>
            <p>Duration: {formatDistanceToNow(new Date(endTime), { addSuffix: true })}</p>
            <p>Started: {formatDistanceToNow(new Date(startTime), { addSuffix: true })}</p>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
} 
