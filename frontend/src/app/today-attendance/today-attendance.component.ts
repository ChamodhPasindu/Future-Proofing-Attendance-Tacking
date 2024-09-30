import { Component, OnInit } from '@angular/core';
import { AttendanceService } from '../attendance.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-today-attendance',
  templateUrl: './today-attendance.component.html',
  styleUrls: ['./today-attendance.component.scss'],
})
export class TodayAttendanceComponent implements OnInit {
  todayAttendance :any[]=[]

  displayedColumns: string[] = [ 'id' ,'name', 'inTime', 'outTime','status'];

  constructor(private service: AttendanceService,private toastr: ToastrService) {}
  ngOnInit(): void {
    this.service.getAllTodayAttendance().subscribe({
      next: (res) => {
        if(!res.data.length){
          this.toastr.error('No any record found','Empty Results');
          return;
        }
        this.todayAttendance = res.data;
      },
      error: (err) => {
        this.toastr.error('Oops,Something went wrong','System Error');
      },
    });
  }
}
