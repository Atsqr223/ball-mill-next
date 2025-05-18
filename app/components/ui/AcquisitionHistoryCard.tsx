'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';

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
  const router = useRouter();

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-yellow-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const handleClick = () => {
    router.push(`/locations/${locationId}/acquisitions/${id}`);
  };

  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={handleClick}
    >
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-semibold truncate">
            {fileName || `Session #${id}`}
          </CardTitle>
          <Badge variant="outline" className={getStatusColor(status)}>
            {status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Sensor Type:</span>
            <span className="font-medium">{sensorType}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Data Points:</span>
            <span className="font-medium">{numDataPoints}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Duration:</span>
            <span className="font-medium">
              {formatDistanceToNow(new Date(endTime), { addSuffix: false })}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Started:</span>
            <span className="font-medium">
              {formatDistanceToNow(new Date(startTime), { addSuffix: true })}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 
