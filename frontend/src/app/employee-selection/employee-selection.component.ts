import { Component, OnInit } from '@angular/core';
import { MatDatepicker } from '@angular/material/datepicker';
import * as moment from 'moment';
import { Moment } from 'moment';
import { AttendanceService } from '../attendance.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-employee-selection',
  templateUrl: './employee-selection.component.html',
  styleUrls: ['./employee-selection.component.scss'],
})
export class EmployeeSelectionComponent implements OnInit {
  employees: any[] = [];

  displayedColumns: string[] = ['date', 'inTime', 'outTime', 'status'];

  selectedYear: number | null = null;
  selectedMonth: number | null = null;

  selectedEmployee: any;
  selectedDate: any;

  attendance: any[]=[];

  constructor(private service: AttendanceService,private toastr: ToastrService) {}

  ngOnInit(): void {
    this.service.getAllEmployees().subscribe({
      next: (res) => {
        if(!res.data.length){
          this.toastr.error('No any employee record found','Empty Results');
          return;
        }
        this.employees = res.data;
      },
      error: (err) => {
        this.toastr.error('Oops,Something went wrong','System Error');
      },
    });
  }

  viewAttendance() {
    this.selectedYear = this.selectedDate.year();
    this.selectedMonth = this.selectedDate.month() + 1;
    this.service.getEmployeeAttendance(this.selectedEmployee.id,this.selectedYear!,this.selectedMonth!).subscribe({
      next: (res) => {
        if(!res.data.length){
          this.toastr.error('No any record found','Empty Results');
          return;
        }
        this.attendance = res.data;
      },
      error: (err) => {
        this.toastr.error('Oops,Something went wrong','System Error');
      },
    });
  }

  chosenMonthHandler(normalizedMonth: Date, datepicker: MatDatepicker<Moment>) {
    this.selectedYear = normalizedMonth.getFullYear();
    this.selectedMonth = normalizedMonth.getMonth() + 1;
    console.log(this.selectedDate,this.selectedYear,this.selectedMonth);
    
    datepicker.close();
  }
}
